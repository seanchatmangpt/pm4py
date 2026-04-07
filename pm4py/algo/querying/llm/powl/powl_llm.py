'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

try:
    import dspy
except ImportError:
    raise ImportError(
        "DSPy is required for POWL v2 functionality. Install it with: pip install dspy"
    )

from typing import Dict, Any, Optional
from pm4py.objects.powl.obj import POWL
from pm4py.algo.querying.llm.powl.algorithm import (
    POWLExplainer,
    POWLDiscoverer,
    POWLComparator,
)


def explain_powl(powl_model: POWL, lm=None) -> str:
    """
    Explain a POWL model in plain language using DSPy.

    Parameters
    ----------
    powl_model : POWL
        The POWL model to explain
    lm : dspy.LM, optional
        DSPy language model. If None, uses the globally configured LM.

    Returns
    -------
    str
        Natural language explanation of the POWL model

    Example
    -------
    >>> import pm4py, dspy
    >>> dspy.configure(lm=dspy.LM("openai/gpt-4o", api_key="..."))
    >>> log = pm4py.read_xes("log.xes")
    >>> powl = pm4py.discover_powl(log)
    >>> print(pm4py.llm.explain_powl(powl))
    """
    from pm4py.llm import abstract_powl

    if lm is not None:
        with dspy.context(lm=lm):
            result = POWLExplainer()(powl_description=abstract_powl(powl_model))
    else:
        result = POWLExplainer()(powl_description=abstract_powl(powl_model))

    return result.explanation


def discover_powl_from_description(process_description: str, lm=None) -> str:
    """
    Discover a POWL model string from a natural language process description using DSPy.

    Parameters
    ----------
    process_description : str
        Natural language description of the process
    lm : dspy.LM, optional
        DSPy language model. If None, uses the globally configured LM.

    Returns
    -------
    str
        POWL model string (parse with pm4py.objects.powl.parser.parse_powl_model_string)

    Example
    -------
    >>> import pm4py, dspy
    >>> dspy.configure(lm=dspy.LM("openai/gpt-4o", api_key="..."))
    >>> s = pm4py.llm.discover_powl_from_description("A loan process starting with application...")
    >>> powl = pm4py.objects.powl.parser.parse_powl_model_string(s)
    """
    if lm is not None:
        with dspy.context(lm=lm):
            result = POWLDiscoverer()(process_description=process_description)
    else:
        result = POWLDiscoverer()(process_description=process_description)

    return result.powl_model_string


def compare_powl_models(powl_1: POWL, powl_2: POWL, lm=None) -> Dict[str, Any]:
    """
    Compare two POWL models and identify structural differences using DSPy.

    Parameters
    ----------
    powl_1 : POWL
        First POWL model
    powl_2 : POWL
        Second POWL model
    lm : dspy.LM, optional
        DSPy language model. If None, uses the globally configured LM.

    Returns
    -------
    Dict[str, Any]
        Dictionary with "comparison" (str) and "confidence" (float) keys

    Example
    -------
    >>> import pm4py, dspy
    >>> dspy.configure(lm=dspy.LM("openai/gpt-4o", api_key="..."))
    >>> log = pm4py.read_xes("log.xes")
    >>> result = pm4py.llm.compare_powl_models(pm4py.discover_powl(log), pm4py.discover_powl(log))
    >>> print(result["comparison"])
    """
    from pm4py.llm import abstract_powl

    powl_1_text = abstract_powl(powl_1)
    powl_2_text = abstract_powl(powl_2)

    if lm is not None:
        with dspy.context(lm=lm):
            result = POWLComparator()(
                powl_1_description=powl_1_text,
                powl_2_description=powl_2_text,
            )
    else:
        result = POWLComparator()(
            powl_1_description=powl_1_text,
            powl_2_description=powl_2_text,
        )

    return {"comparison": result.comparison, "confidence": result.confidence}
