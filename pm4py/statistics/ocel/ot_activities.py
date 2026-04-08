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


from pm4py.util import constants
from pm4py.objects.ocel import constants as ocel_constants
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Collection


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE
    TEMP_COLUMN = "temp_column"
    TEMP_SEPARATOR = "temp_separator"


def get_object_type_activities(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> Dict[str, Collection[str]]:
    """
    Gets the set of activities performed for each object type

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.OBJECT_TYPE => the object type column

    Returns
    ----------------
    dict
        A dictionary having as key the object types and as values the activities performed for that object type
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, ocel.event_activity
    )
    object_type_column = exec_utils.get_param_value(
        Parameters.OBJECT_TYPE, parameters, ocel.object_type_column
    )

    matching_dict = {}
    prel_dict = (
        ocel.relations.groupby([activity_key, object_type_column])
        .size()
        .to_dict()
    )

    for el in prel_dict:
        if not el[1] in matching_dict:
            matching_dict[el[1]] = set()
        matching_dict[el[1]].add(el[0])

    return matching_dict
