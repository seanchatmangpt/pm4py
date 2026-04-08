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



import importlib.util


def apply(powl, parameters=None):
    """
    Converts a POWL model to a BPMN model.

    Requires the 'powl' PyPI package: ``pip install pm4py[powl]``.

    Parameters
    ----------
    powl
        POWL model
    parameters
        Parameters of the algorithm

    Returns
    -------
    bpmn_graph
        BPMN model (as a pm4py BPMN object)
    """
    if importlib.util.find_spec("powl") is None:
        raise ImportError(
            "The 'powl' package is required for POWL to BPMN conversion. "
            "Install it with: pip install pm4py[powl]"
        )
    from powl.conversion.variants.to_bpmn import apply as powl_to_bpmn

    bpmn_graph, _, _ = powl_to_bpmn(powl, parameters=parameters)

    from pm4py.objects.bpmn.layout import layouter as bpmn_layouter
    bpmn_graph = bpmn_layouter.apply(bpmn_graph)

    return bpmn_graph
