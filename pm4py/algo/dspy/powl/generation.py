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



import inspect
from func_timeout import func_set_timeout


def _looks_like_powl(powl_string: str, parsed) -> bool:
    """Check if a parsed result represents a meaningful POWL model.

    The POWL parser treats any bare string as a single-activity Transition.
    We reject those — a valid POWL model must contain at least one structural
    element (XOR, LOOP, partial order) or multiple activities.
    """
    from pm4py.objects.powl.obj import Transition, SilentTransition, OperatorPOWL, StrictPartialOrder

    if parsed is None:
        return False

    # Single bare transition is not a valid process model
    if isinstance(parsed, (Transition, SilentTransition)):
        return False

    # Operators, partial orders, decision graphs are valid
    if isinstance(parsed, (OperatorPOWL, StrictPartialOrder)):
        return True

    return True


def validate_powl(powl_string: str) -> dict:
    """Validate a POWL model string by attempting to parse it.

    A valid POWL must contain at least one structural element (XOR, LOOP,
    partial order, etc.). A bare activity label like 'A' is not accepted.

    Returns dict with 'return_value' (parsed model or None) and 'errors'.
    """
    try:
        from pm4py.objects.powl.parser import parse_powl_model_string
        parsed = parse_powl_model_string(powl_string.strip())
        if not _looks_like_powl(powl_string, parsed):
            return {
                "return_value": None,
                "is_valid": False,
                "errors": "POWL must contain structural elements (X, *, PO), not a bare activity label",
            }
        return {"return_value": parsed, "is_valid": True, "errors": None}
    except Exception as e:
        return {"return_value": None, "is_valid": False, "errors": str(e)}


def check_activity_coverage(powl_string: str, expected_activities: list) -> dict:
    """Check if all expected activity labels appear in the POWL string.

    Returns dict with 'return_value' (set of missing activities or None) and 'errors'.
    """
    try:
        missing = []
        for activity in expected_activities:
            if (f"'{activity}'" not in powl_string
                    and f'"{activity}"' not in powl_string
                    and activity not in powl_string):
                missing.append(activity)
        if missing:
            return {"return_value": missing, "errors": f"Missing activities: {', '.join(missing)}"}
        return {"return_value": None, "errors": None}
    except Exception as e:
        return {"return_value": None, "errors": str(e)}


def check_fitness(powl_string: str, log_obj) -> dict:
    """Check token-based replay fitness of a POWL model against a log.

    Returns dict with 'return_value' (fitness float) and 'errors'.
    """
    try:
        import pm4py
        from pm4py.objects.powl.parser import parse_powl_model_string
        from pm4py.objects.conversion.powl.converter import apply as powl_to_pn

        parsed = parse_powl_model_string(powl_string)
        net, im, fm = powl_to_pn(parsed)
        result = pm4py.fitness_token_based_replay(log_obj, net, im, fm)
        fitness = float(result.get("average_trace_fitness", 0.0))
        return {"return_value": fitness, "errors": None}
    except Exception as e:
        return {"return_value": None, "errors": str(e)}


def finish(powl_model: str) -> str:
    """Conclude the trajectory and return the final POWL model string."""
    return powl_model


def fn_metadata(func):
    """Extract function signature and docstring as metadata for the agent."""
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func) or "No docstring."
    return dict(function_name=func.__name__, arguments=str(signature), docstring=docstring)


def wrap_function_with_timeout(fn, timeout: int = 30):
    """Wrap a function with a timeout to prevent hanging."""
    @func_set_timeout(timeout)
    def wrapper(*args, **kwargs):
        try:
            return {"return_value": fn(*args, **kwargs), "errors": None}
        except Exception as e:
            return {"return_value": None, "errors": str(e)}
    return wrapper
