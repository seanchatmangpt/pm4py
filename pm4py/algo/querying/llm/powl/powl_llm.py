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
        "DSPy is required for POWL v2 functionality. Install it with: pip install dspy-ai"
    )

from typing import Dict, Any, Optional
from pm4py.objects.powl.obj import POWL
from pm4py.algo.querying.llm.powl.algorithm import (
    POWLExplainer,
    POWLDiscoverer,
    POWLComparator,
)


def explain_powl(powl_model: POWL, lm: Optional[Any] = None) -> str:
    """
    Explain a POWL model in plain language using DSPy.

    Parameters
    ----------
    powl_model : POWL
        The POWL model to explain
    lm : Optional[dspy.LM]
        DSPy language model to use. If None, uses dspy.settings.lm

    Returns
    -------
    str
        Natural language explanation of the POWL model

    Example
    -------
    >>> import pm4py
    >>> import dspy
    >>> dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", api_key="..."))
    >>> log = pm4py.read_xes("log.xes")
    >>> powl = pm4py.discover_powl(log)
    >>> explanation = pm4py.llm.explain_powl(powl)
    >>> print(explanation)
    """
    from pm4py.llm import abstract_powl

    if lm is None:
        lm = dspy.settings.lm

    with dspy.context(lm=lm):
        explainer = POWLExplainer()
        powl_text = abstract_powl(powl_model)
        result = explainer(powl_description=powl_text)
        return result.explanation


def discover_powl_from_description(
    process_description: str, lm: Optional[Any] = None
) -> str:
    """
    Discover a POWL model string from a natural language process description using DSPy.

    Parameters
    ----------
    process_description : str
        Natural language description of the process
    lm : Optional[dspy.LM]
        DSPy language model to use. If None, uses dspy.settings.lm

    Returns
    -------
    str
        POWL model string (can be parsed with pm4py.objects.powl.parser.parse_powl_model_string)

    Example
    -------
    >>> import pm4py
    >>> import dspy
    >>> dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", api_key="..."))
    >>> desc = "A process starts with activity A, then either B or C in parallel, then D at the end."
    >>> powl_string = pm4py.llm.discover_powl_from_description(desc)
    >>> powl_model = pm4py.objects.powl.parser.parse_powl_model_string(powl_string)
    """
    if lm is None:
        lm = dspy.settings.lm

    with dspy.context(lm=lm):
        discoverer = POWLDiscoverer()
        result = discoverer(process_description=process_description)
        return result.powl_model_string


def compare_powl_models(
    powl_1: POWL, powl_2: POWL, lm: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Compare two POWL models and identify structural differences using DSPy.

    Parameters
    ----------
    powl_1 : POWL
        First POWL model
    powl_2 : POWL
        Second POWL model
    lm : Optional[dspy.LM]
        DSPy language model to use. If None, uses dspy.settings.lm

    Returns
    -------
    Dict[str, Any]
        Dictionary with keys:
        - "comparison": detailed textual comparison of the models
        - "confidence": confidence in the comparison (0.0 to 1.0)

    Example
    -------
    >>> import pm4py
    >>> import dspy
    >>> dspy.settings.configure(lm=dspy.OpenAI(model="gpt-4", api_key="..."))
    >>> log = pm4py.read_xes("log.xes")
    >>> powl_1 = pm4py.discover_powl(log)
    >>> powl_2 = pm4py.discover_powl(log, variant=POWLDiscoveryVariant.MAXIMAL_ORDER)
    >>> result = pm4py.llm.compare_powl_models(powl_1, powl_2)
    >>> print(result["comparison"])
    >>> print(f"Confidence: {result['confidence']}")
    """
    from pm4py.llm import abstract_powl

    if lm is None:
        lm = dspy.settings.lm

    with dspy.context(lm=lm):
        comparator = POWLComparator()
        powl_1_text = abstract_powl(powl_1)
        powl_2_text = abstract_powl(powl_2)
        result = comparator(
            powl_1_description=powl_1_text, powl_2_description=powl_2_text
        )
        return {"comparison": result.comparison, "confidence": result.confidence}
