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
from pm4py.objects.ocel.util import ocel_consistency
from pm4py.objects.ocel.util import filtering_utils
from enum import Enum
from pm4py.util import exec_utils, constants as pm4_constants


class Parameters(Enum):
    ENCODING = "encoding"


def apply(
    ocel: OCEL,
    output_path: str,
    objects_path=None,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Exports an object-centric event log in a CSV file, using Pandas as backend

    Parameters
    -----------------
    ocel
        Object-centric event log
    output_path
        Destination file
    objects_path
        Optional path, where the objects dataframe is stored
    parameters
        Parameters of the algorithm
    """
    if parameters is None:
        parameters = {}

    encoding = exec_utils.get_param_value(
        Parameters.ENCODING, parameters, pm4_constants.DEFAULT_ENCODING
    )

    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(
        ocel, parameters=parameters
    )

    ocel.get_extended_table().to_csv(
        output_path, index=False, na_rep="", encoding=encoding
    )

    if objects_path is not None:
        ocel.objects.to_csv(
            objects_path, index=False, na_rep="", encoding=encoding
        )
