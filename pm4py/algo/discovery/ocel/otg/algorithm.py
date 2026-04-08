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


from pm4py.algo.discovery.ocel.otg.variants import classic
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Tuple, Set


class Variants(Enum):
    CLASSIC = classic


def apply(ocel: OCEL,
          variant=Variants.CLASSIC,
          parameters: Optional[Dict[Any,
                                    Any]] = None) -> Tuple[Set[str],
                                                           Dict[Tuple[str,
                                                                str,
                                                                str],
                                                                int]]:
    """
    Discovers an OTG (object-type-graph) from the provided OCEL

    Published in: https://publications.rwth-aachen.de/record/1014107

    Parameters
    -----------------
    ocel
        OCEL
    variant
        Variant to be used (available: Variants.CLASSIC)
    parameters
        Variant-specific parameters

    Returns
    -----------------
    otg
        Object-type-graph (tuple; the first element is the set of object types, the second element is the OTG)
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters)
