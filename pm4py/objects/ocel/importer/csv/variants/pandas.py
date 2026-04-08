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


from typing import Optional, Dict, Any

from pm4py.objects.ocel.obj import OCEL
from pm4py.objects.ocel.util import extended_table
from pm4py.objects.ocel.util import ocel_consistency
from enum import Enum
from pm4py.util import exec_utils, constants as pm4_constants, pandas_utils


class Parameters(Enum):
    ENCODING = "encoding"


def apply(
    file_path: str,
    objects_path: str = None,
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Imports an object-centric event log from a CSV file, using Pandas as backend

    Parameters
    -----------------
    file_path
        Path to the object-centric event log
    objects_path
        Optional path to a CSV file containing the objects dataframe
    parameters
        Parameters of the algorithm

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING)
    table = pandas_utils.read_csv(file_path, index_col=False, encoding=encoding, dtype=str)

    objects = None
    if objects_path is not None:
        objects = pandas_utils.read_csv(objects_path, index_col=False, encoding=encoding, dtype=str)

    ocel = extended_table.get_ocel_from_extended_table(
        table, objects, parameters=parameters
    )
    ocel = ocel_consistency.apply(ocel, parameters=parameters)

    return ocel
