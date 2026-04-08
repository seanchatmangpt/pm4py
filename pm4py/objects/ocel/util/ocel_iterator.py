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
from pm4py.util import exec_utils
from pm4py.objects.ocel import constants as ocel_constants
import pandas as pd


class Parameters(Enum):
    OCEL_TYPE_PREFIX = ocel_constants.PARAM_OBJECT_TYPE_PREFIX_EXTENDED


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Creates an iterator over the events of an object-centric event log

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the method, including:
        - Parameters.OCEL_TYPE_PREFIX => the prefix of the object types in the OCEL (default: ocel:type)

    Returns
    ----------------
    yielded event
        The events of the OCEL, one by one.
    """
    if parameters is None:
        parameters = {}

    ot_prefix = exec_utils.get_param_value(
        Parameters.OCEL_TYPE_PREFIX,
        parameters,
        ocel_constants.DEFAULT_OBJECT_TYPE_PREFIX_EXTENDED,
    )

    ext_table = ocel.get_extended_table(ot_prefix)

    for k, ev in ext_table.iterrows():
        yield {
            x: y
            for x, y in dict(ev).items()
            if isinstance(y, list) or not pd.isna(y)
        }
