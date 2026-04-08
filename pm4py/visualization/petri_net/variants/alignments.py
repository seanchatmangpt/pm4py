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


from pm4py.visualization.petri_net.common import visualize
from pm4py.visualization.petri_net.util import alignments_decoration
from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Optional, Dict, Any


def apply(
    net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
    log=None,
    aggregated_statistics=None,
    parameters: Optional[Dict[Any, Any]] = None,
) -> str:
    """
    Apply method for Petri net visualization (it calls the
    graphviz_visualization method)

    Parameters
    -----------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    log
        (Optional) log
    aggregated_statistics
        Dictionary containing the frequency statistics
    parameters
        Algorithm parameters

    Returns
    -----------
    viz
        Graph object
    """
    if aggregated_statistics is None and log is not None:
        aggregated_statistics = (
            alignments_decoration.get_alignments_decoration(
                net, initial_marking, final_marking, log=log
            )
        )

    return visualize.apply(
        net,
        initial_marking,
        final_marking,
        parameters=parameters,
        decorations=aggregated_statistics,
    )
