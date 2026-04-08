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
from typing import Optional, Dict, Any, Tuple
from copy import deepcopy


def apply(net: PetriNet, initial_marking: Marking, final_marking: Marking, string_dictio: Dict[str, str], parameters: Optional[Dict[Any, Any]] = None) -> Tuple[PetriNet, Marking, Marking]:
    """
    Replaces the labels in the provided accepting Petri net using the provided correspondence dictionary.

    Parameters
    ----------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    string_dictio
        Correspondence dictionary (old labels -> new labels)

    Returns
    ----------------
    net
        Petri net
    initial_marking
        Initial marking
    final_marking
        Final marking
    """
    if parameters is None:
        parameters = {}

    net, initial_marking, final_marking = deepcopy([net, initial_marking, final_marking])

    for trans in net.transitions:
        if trans.label is not None and trans.label in string_dictio:
            trans.label = string_dictio[trans.label]

    return net, initial_marking, final_marking
