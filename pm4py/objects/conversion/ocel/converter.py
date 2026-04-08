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



from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.objects.conversion.ocel.variants import (
    ocel_to_nx,
    ocel_features_to_nx,
)


class Variants(Enum):
    OCEL_TO_NX = ocel_to_nx
    OCEL_FEATURES_TO_NX = ocel_features_to_nx


def apply(
    ocel: OCEL,
    variant=Variants.OCEL_TO_NX,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Converts an OCEL to another object.

    Parameters
    -------------
    ocel
        Object-centric event log
    variant
        Variant of the algorithm to use, posible values:
        - Variants.OCEL_TO_NX: graph containing event and object IDS and two type of relations (REL=related objects, DF=directly-follows)
        - Variants.OCEL_FEATURES_TO_NX: graph containing different types of interconnection at the object level
    parameters
        Variant-specific parameters
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(ocel, parameters=parameters)
