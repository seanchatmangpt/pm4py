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


from collections import defaultdict
from typing import Optional, Dict, Any, Tuple, Set
from pm4py.objects.ocel.obj import OCEL
from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.discovery.ocel.etot.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(ocel: OCEL,
          variant=Variants.CLASSIC,
          parameters: Optional[Dict[Any,
                                    Any]] = None) -> Tuple[Set[str],
                                                           Set[str],
                                                           Set[Tuple[str,
                                                                     str]],
                                                           Dict[Tuple[str,
                                                                      str],
                                                                int]]:
    """
    Discovers the ET-OT graph from an OCEL

    Published in: https://publications.rwth-aachen.de/record/1014107

    Parameters
    ---------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to be used (available: Variants.CLASSIC)
    parameters
        Variant-specific parameters

    Returns
    ----------------
    activities
        Set of activities
    object_types
        Set of object types
    edges
        Set of edges
    edges_frequency
        Dictionary associating to each edge a frequency
    """
    return exec_utils.get_variant(variant).apply(ocel, parameters)
