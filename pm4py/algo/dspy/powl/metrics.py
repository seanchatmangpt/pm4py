"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""



import re


def _normalize_powl(s: str) -> str:
    """Normalize a POWL string for comparison.

    Strips whitespace, normalizes quotes, removes extra spaces.
    """
    s = s.strip().replace("\n", "").replace("\r", "").replace("\t", "")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


def parse_only_metric(example, pred, trace=None):
    """Strict metric: checks if the predicted POWL string parses successfully.

    This is the lightweight metric that doesn't require an event log for
    conformance checking. Use this for initial development and testing.

    Returns 1.0 if parseable, 0.0 otherwise.
    """
    pred_str = str(pred.answer).strip() if hasattr(pred, "answer") else ""
    if not pred_str:
        return 0.0

    try:
        from pm4py.objects.powl.parser import parse_powl_model_string
        from pm4py.objects.powl.obj import Transition, SilentTransition
        parsed = parse_powl_model_string(pred_str)
        if parsed is None:
            return 0.0
        # Bare transition label is not a valid process model
        if isinstance(parsed, (Transition, SilentTransition)):
            return 0.0
        return 1.0
    except Exception:
        return 0.0


def structural_metric(example, pred, trace=None):
    """Metric checking parse validity AND activity coverage.

    Returns 1.0 if parseable AND all expected activities are present.
    Returns 0.5 if parseable but missing activities.
    Returns 0.0 if unparseable.
    """
    pred_str = str(pred.answer).strip() if hasattr(pred, "answer") else ""
    if not pred_str:
        return 0.0

    # Check parse validity
    try:
        from pm4py.objects.powl.parser import parse_powl_model_string
        from pm4py.objects.powl.obj import Transition, SilentTransition
        parsed = parse_powl_model_string(pred_str)
        if parsed is None:
            return 0.0
        if isinstance(parsed, (Transition, SilentTransition)):
            return 0.0
    except Exception:
        return 0.0

    # Check activity coverage if expected activities are available
    expected = getattr(example, "expected_activities", None)
    if expected:
        expected_set = set(expected) if not isinstance(expected, set) else expected
        found = 0
        for activity in expected_set:
            if (f"'{activity}'" in pred_str
                    or '"' + activity + '"' in pred_str
                    or activity in pred_str):
                found += 1
        coverage = found / len(expected_set) if expected_set else 1.0
        return 0.5 + 0.5 * coverage

    return 1.0


def conformance_metric(example, pred, trace=None):
    """Full conformance metric: validity + fitness + precision.

    Requires 'event_log' in the example. Returns weighted composite score:
    - 40% parse validity
    - 30% fitness
    - 30% precision

    Falls back to structural_metric if no event_log available.
    """
    pred_str = str(pred.answer).strip() if hasattr(pred, "answer") else ""
    if not pred_str:
        return 0.0

    # Parse check
    try:
        from pm4py.objects.powl.parser import parse_powl_model_string
        from pm4py.objects.powl.obj import Transition, SilentTransition
        parsed = parse_powl_model_string(pred_str)
        if parsed is None:
            return 0.0
        if isinstance(parsed, (Transition, SilentTransition)):
            return 0.0
    except Exception:
        return 0.0

    # Get event log from example
    log_obj = getattr(example, "event_log", None)
    if log_obj is None:
        return structural_metric(example, pred, trace)

    # Fitness
    try:
        import pm4py
        from pm4py.objects.conversion.powl.converter import apply as powl_to_pn

        net, im, fm = powl_to_pn(parsed)
        result = pm4py.fitness_token_based_replay(log_obj, net, im, fm)
        fitness = float(result.get("average_trace_fitness", 0.0))
    except Exception:
        fitness = 0.0

    # Precision
    try:
        import pm4py
        precision = float(pm4py.precision_token_based_replay(log_obj, net, im, fm))
    except Exception:
        precision = 0.0

    return 0.40 * 1.0 + 0.30 * fitness + 0.30 * precision


def exact_match_metric(example, pred, trace=None):
    """Strictest metric: exact string match after normalization.

    Use this when ground truth POWL strings are available in the example.
    """
    pred_str = _normalize_powl(str(pred.answer)) if hasattr(pred, "answer") else ""
    gold_str = _normalize_powl(str(example.powl_model)) if hasattr(example, "powl_model") else ""
    return pred_str == gold_str
