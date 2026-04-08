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


from pm4py.objects.conversion.trie.variants import to_petri_net
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.trie.obj import Trie
from typing import Optional, Dict, Any, Tuple


class Variants(Enum):
    TO_PETRI_NET = to_petri_net


def apply(
    prefix_tree: Trie,
    variant=Variants.TO_PETRI_NET,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[PetriNet, Marking, Marking]:
    """
    Converts the prefix tree objects using the specified variant

    Parameters
    ----------------
    prefix_tree
        Prefix tree
    variant
        Variant of the conversion:
        - Variants.TO_PETRI_NET => converts the prefix tree object to a Petri net
    parameters
        Optional parameters of the method.

    Returns
    ----------------
    obj
        Converted object
    """
    return exec_utils.get_variant(variant).apply(prefix_tree, parameters)
