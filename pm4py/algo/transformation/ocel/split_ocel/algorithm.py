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


from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from enum import Enum
from pm4py.algo.transformation.ocel.split_ocel.variants import (
    connected_components,
    ancestors_descendants,
)
from pm4py.util import exec_utils


class Variants(Enum):
    CONNECTED_COMPONENTS = connected_components
    ANCESTORS_DESCENDANTS = ancestors_descendants


def apply(
    ocel: OCEL,
    variant=Variants.CONNECTED_COMPONENTS,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Splits an OCEL into sub-OCELs using a given criteria (variant).

    Parameters
    ----------------
    ocel
        OCEL
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.CONNECTED_COMPONENTS

    Returns
    ----------------
    splitted_ocel
        List of OCELs found based on the connected components
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters)
