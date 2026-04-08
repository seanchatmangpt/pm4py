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
from pm4py.util import exec_utils, constants
from pm4py.objects.ocel.util import filtering_utils
from copy import copy
from typing import Dict, Any, Optional, Collection
from pm4py.objects.ocel.obj import OCEL


class Parameters(Enum):
    ATTRIBUTE_KEY = constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY
    POSITIVE = "positive"


def apply(
    ocel: OCEL,
    values: Collection[Any],
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Filters the object-centric event log on the provided object attributes values

    Parameters
    ----------------
    ocel
        Object-centric event log
    values
        Collection of values
    parameters
        Parameters of the algorithm, including:
        - Parameters.ATTRIBUTE_KEY => the attribute that should be filtered
        - Parameters.POSITIVE => decides if the values should be kept (positive=True) or removed (positive=False)

    Returns
    ----------------
    ocel
        Filtered object-centric event log
    """
    if parameters is None:
        parameters = {}

    attribute_key = exec_utils.get_param_value(
        Parameters.ATTRIBUTE_KEY, parameters, ocel.object_type_column
    )
    positive = exec_utils.get_param_value(
        Parameters.POSITIVE, parameters, True
    )

    ocel = copy(ocel)
    if positive:
        ocel.objects = ocel.objects[ocel.objects[attribute_key].isin(values)]
    else:
        ocel.objects = ocel.objects[~ocel.objects[attribute_key].isin(values)]

    return filtering_utils.propagate_object_filtering(
        ocel, parameters=parameters
    )
