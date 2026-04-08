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



from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import reachability_graph
from typing import Optional, Dict, Any
from pm4py.util import nx_utils


def apply(
    petri_net: PetriNet,
    im: Optional[Marking] = None,
    parameters: Optional[Dict[Any, Any]] = None,
) -> float:
    """
    Computes the extended cyclomatic metric as described in the paper:

    "Complexity Metrics for Workflow Nets"
    Lassen, Kristian Bisgaard, and Wil MP van der Aalst

    Parameters
    -------------
    petri_net
        Petri net

    Returns
    -------------
    ext_cyclomatic_metric
        Extended Cyclomatic metric
    """
    if parameters is None:
        parameters = {}

    if im is None:
        # if not provided, try to reconstruct the initial marking by taking the
        # places with empty preset
        im = Marking()
        for place in petri_net.places:
            if len(place.in_arcs) == 0:
                im[place] = 1

    reach_graph = reachability_graph.construct_reachability_graph(
        petri_net, im, use_trans_name=True
    )

    G = nx_utils.DiGraph()
    for n in reach_graph.states:
        G.add_node(n.name)

    for n in reach_graph.states:
        for n2 in n.outgoing:
            G.add_edge(n.name, n2.name)

    sg = list(nx_utils.strongly_connected_components(G))

    return len(G.edges) - len(G.nodes) + len(sg)
