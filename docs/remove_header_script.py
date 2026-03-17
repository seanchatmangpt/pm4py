import re
from pathlib import Path
from typing import Optional


SKIP_DIRS = {".git", "__pycache__", ".mypy_cache", ".pytest_cache"}
ENCODING_PATTERN = re.compile(r"#.*coding[:=]\s*[-\w.]+")
COPYRIGHT_LINE_PATTERN = re.compile(
    r"Copyright \(C\) \d{4} Process Intelligence Solutions UG \(haftungsbeschränkt\)"
)
COPYRIGHT_LINE_CANONICAL = "Copyright (C) <YEAR> Process Intelligence Solutions UG (haftungsbeschränkt)"


def _consume_prefix(data: str) -> int:
    index = 0

    if data.startswith("\ufeff"):
        index = 1

    while True:
        if data.startswith("#!", index):
            line_end = data.find("\n", index)
            if line_end == -1:
                return len(data)
            index = line_end + 1
            continue

        line_end = data.find("\n", index)
        if line_end == -1:
            line_end = len(data)
        line = data[index:line_end]
        if ENCODING_PATTERN.match(line):
            if line_end < len(data):
                line_end += 1
            index = line_end
            continue

        break

    return index


def _strip_wrapping_triple_quotes(data: str) -> str:
    stripped = data.strip()
    if len(stripped) >= 6 and (
        (stripped.startswith('"""') and stripped.endswith('"""'))
        or (stripped.startswith("'''") and stripped.endswith("'''"))
    ):
        return stripped[3:-3]
    return stripped


def _normalize_header(data: str) -> str:
    normalized = _strip_wrapping_triple_quotes(data).strip()
    return COPYRIGHT_LINE_PATTERN.sub(COPYRIGHT_LINE_CANONICAL, normalized)


def remove_header(data: str, expected_header: str) -> Optional[str]:
    header_start = _consume_prefix(data)
    while header_start < len(data) and data[header_start] in {" ", "\t", "\r", "\n"}:
        header_start += 1

    if not (data.startswith('"""', header_start) or data.startswith("'''", header_start)):
        return None

    quote = data[header_start:header_start + 3]
    header_end = data.find(quote, header_start + 3)
    if header_end == -1:
        return None

    header_content = data[header_start + 3:header_end]
    if _normalize_header(header_content) != expected_header:
        return None

    cut_end = header_end + 3
    if data.startswith("\r\n", cut_end):
        cut_end += 2
    elif data.startswith("\n", cut_end):
        cut_end += 1

    return data[:header_start] + data[cut_end:]


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    repository_root = script_dir.parent
    license_header = _normalize_header((script_dir / "LICENSE_HEADER_GITHUB.txt").read_text(encoding="utf-8"))
    python_files = sorted(repository_root.rglob("*.py"))

    for filename in python_files:
        if any(part in SKIP_DIRS for part in filename.parts):
            continue

        try:
            data = filename.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print("skipping non utf-8 file: " + str(filename.relative_to(repository_root)))
            continue

        updated_data = remove_header(data, license_header)
        if updated_data is None:
            print("skipping: " + str(filename.relative_to(repository_root)))
            continue

        filename.write_text(updated_data, encoding="utf-8")
        print("removing header from: " + str(filename.relative_to(repository_root)))
