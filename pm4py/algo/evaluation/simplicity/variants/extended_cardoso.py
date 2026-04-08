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



from pm4py.objects.petri_net.obj import PetriNet
from typing import Optional, Dict, Any


def apply(
    petri_net: PetriNet, parameters: Optional[Dict[Any, Any]] = None
) -> float:
    """
    Computes the extended Cardoso metric as described in the paper:

    "Complexity Metrics for Workflow Nets"
    Lassen, Kristian Bisgaard, and Wil MP van der Aalst

    Parameters
    -------------
    petri_net
        Petri net

    Returns
    -------------
    ext_cardoso_metric
        Extended Cardoso metric
    """
    if parameters is None:
        parameters = {}

    ext_card = 0

    for place in petri_net.places:
        targets = set()
        for out_arc in place.out_arcs:
            targets1 = set()
            for out_arc2 in out_arc.target.out_arcs:
                targets1.add(out_arc2.target.name)
            targets.add(tuple(sorted(list(targets1))))
        ext_card += len(targets)

    return ext_card
