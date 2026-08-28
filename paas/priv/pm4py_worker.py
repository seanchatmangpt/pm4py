#!/usr/bin/env python3
"""Bounded PM4Py execution adapter. No arbitrary module/function execution."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

OPERATIONS = {"read_xes_summary", "discover_dfg"}
RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def emit(value: dict[str, Any], status: int = 0) -> None:
    sys.stdout.write(json.dumps(value, sort_keys=True, separators=(",", ":")))
    sys.stdout.flush()
    raise SystemExit(status)


def refuse(code: str, detail: Any, status: int = 64) -> None:
    emit({"status": "REFUSED", "code": code, "detail": detail}, status)


def decode_request(encoded: str) -> dict[str, Any]:
    padding = "=" * (-len(encoded) % 4)
    try:
        value = json.loads(base64.urlsafe_b64decode(encoded + padding))
    except Exception as exc:  # noqa: BLE001 - typed refusal at process boundary
        refuse("REFUSED_INVALID_REQUEST_ENCODING", str(exc))
    if not isinstance(value, dict):
        refuse("REFUSED_INVALID_REQUEST", "request must be a JSON object")
    return value


def resolve_input(raw: str, root: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    root = root.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        refuse("REFUSED_INPUT_OUTSIDE_DATA_ROOT", str(path))
    if not path.is_file():
        refuse("REFUSED_INPUT_NOT_FOUND", str(path))
    if path.suffix.lower() != ".xes":
        refuse("REFUSED_UNSUPPORTED_INPUT_FORMAT", path.suffix)
    return path


def import_pm4py():
    try:
        import pm4py  # type: ignore
    except Exception as exc:  # noqa: BLE001
        refuse("REFUSED_PM4PY_UNAVAILABLE", str(exc), 69)
    return pm4py


def read_xes_summary(pm4py: Any, path: Path) -> dict[str, Any]:
    log = pm4py.read_xes(str(path))
    activities: dict[str, int] = {}
    event_count = 0
    for trace in log:
        for event in trace:
            event_count += 1
            activity = str(event.get("concept:name", ""))
            activities[activity] = activities.get(activity, 0) + 1
    return {
        "trace_count": len(log),
        "event_count": event_count,
        "activities": dict(sorted(activities.items())),
    }


def discover_dfg(pm4py: Any, path: Path) -> dict[str, Any]:
    log = pm4py.read_xes(str(path))
    dfg, starts, ends = pm4py.discover_dfg(log)
    edges = sorted(
        ({"source": str(source), "target": str(target), "count": int(count)} for (source, target), count in dfg.items()),
        key=lambda edge: (edge["source"], edge["target"]),
    )
    return {
        "edges": edges,
        "start_activities": dict(sorted((str(k), int(v)) for k, v in starts.items())),
        "end_activities": dict(sorted((str(k), int(v)) for k, v in ends.items())),
    }


def verify_replay(final_dir: Path, operation: str, input_digest: str, source_sha: str) -> dict[str, Any]:
    receipt_path = final_dir / "receipt.json"
    result_path = final_dir / "result.json"
    if not receipt_path.is_file() or not result_path.is_file():
        refuse("REFUSED_INCOMPLETE_REPLAY_CAPSULE", str(final_dir))
    receipt = json.loads(receipt_path.read_text())
    result = json.loads(result_path.read_text())
    expected = {
        "operation": operation,
        "input_sha256": input_digest,
        "source_sha": source_sha,
    }
    actual = {key: receipt.get(key) for key in expected}
    if actual != expected:
        refuse("REFUSED_REPLAY_SUBJECT_MISMATCH", {"expected": expected, "actual": actual})
    if receipt.get("result_sha256") != sha256_bytes(canonical(result)):
        refuse("REFUSED_REPLAY_DIGEST_MISMATCH", str(final_dir))
    return {"status": "ALIVE", "replay": True, "result": result, "receipt": receipt}


def execute(request: dict[str, Any]) -> dict[str, Any]:
    operation = request.get("operation")
    run_id = request.get("run_id")
    raw_path = request.get("input_path")

    if operation not in OPERATIONS:
        refuse("REFUSED_UNSUPPORTED_OPERATION", operation)
    if not isinstance(run_id, str) or not RUN_ID.fullmatch(run_id):
        refuse("REFUSED_INVALID_RUN_ID", run_id)
    if not isinstance(raw_path, str) or not raw_path:
        refuse("REFUSED_INVALID_INPUT_PATH", raw_path)

    root = Path(os.environ.get("PM4PY_DATA_ROOT", "/app/data")).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = resolve_input(raw_path, root)
    input_digest = sha256_file(path)
    source_sha = os.environ.get("PM4PY_SOURCE_SHA", "UNKNOWN")
    final_dir = root / "runs" / run_id

    if final_dir.exists():
        return verify_replay(final_dir, operation, input_digest, source_sha)

    pm4py = import_pm4py()
    if operation == "read_xes_summary":
        result = read_xes_summary(pm4py, path)
    elif operation == "discover_dfg":
        result = discover_dfg(pm4py, path)
    else:  # admission above makes this unreachable
        refuse("REFUSED_UNSUPPORTED_OPERATION", operation)

    result_bytes = canonical(result)
    receipt = {
        "schema": "urn:pm4py-paas:receipt:v1",
        "standing": "ALIVE",
        "authority": "BRCE",
        "run_id": run_id,
        "operation": operation,
        "input_sha256": input_digest,
        "result_sha256": sha256_bytes(result_bytes),
        "pm4py_version": getattr(pm4py, "__version__", "UNKNOWN"),
        "source_sha": source_sha,
    }

    runs_dir = root / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = runs_dir / f".tmp-{run_id}-{os.getpid()}"
    temp_dir.mkdir(mode=0o700)
    try:
        (temp_dir / "result.json").write_bytes(result_bytes + b"\n")
        (temp_dir / "receipt.json").write_bytes(canonical(receipt) + b"\n")
        try:
            os.replace(temp_dir, final_dir)
        except OSError:
            # Another execution with the same run identity may have won the atomic publish race.
            # The winner is authoritative only if its receipt binds to this exact admitted subject.
            if final_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
                return verify_replay(final_dir, operation, input_digest, source_sha)
            raise
    except Exception as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        refuse("REFUSED_CAPSULE_PUBLISH_FAILED", str(exc), 74)

    return {"status": "ALIVE", "replay": False, "result": result, "receipt": receipt}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-base64", required=True)
    args = parser.parse_args()
    emit(execute(decode_request(args.request_base64)))


if __name__ == "__main__":
    main()
