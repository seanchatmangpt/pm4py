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


def apply(powl, parameters=None):
    """
    Converts a POWL model to a BPMN model via ProcessTree.

    Pipeline: POWL → ProcessTree → BPMN.

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
    from pm4py.objects.conversion.powl.variants.to_process_tree import apply as to_pt
    from pm4py.convert import convert_to_bpmn

    pt = to_pt(powl)
    bpmn_graph = convert_to_bpmn(pt)

    return bpmn_graph
