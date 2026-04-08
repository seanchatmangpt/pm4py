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
from pm4py.util import exec_utils, pandas_utils
from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel import constants as ocel_constants
from typing import Optional, Dict, Any


class Parameters(Enum):
    EVENT_ID = ocel_constants.PARAM_EVENT_ID
    OBJECT_TYPE = ocel_constants.PARAM_OBJECT_TYPE


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Returns for each object type the number of events related to at least one object of the given type.

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.EVENT_ID => the event identifier
        - Parameters.OBJECT_TYPE => the object type column

    Returns
    -----------------
    dictio
        Dictionary associating to each object type the number of events related to at least one object of the given
        type.
    """
    if parameters is None:
        parameters = {}

    event_id = exec_utils.get_param_value(
        Parameters.EVENT_ID, parameters, ocel.event_id_column
    )
    object_type = exec_utils.get_param_value(
        Parameters.OBJECT_TYPE, parameters, ocel.object_type_column
    )

    object_types = pandas_utils.format_unique(
        ocel.objects[object_type].unique()
    )

    ret = {}

    for ot in object_types:
        ret[ot] = ocel.relations[ocel.relations[object_type] == ot][
            event_id
        ].nunique()

    return ret
