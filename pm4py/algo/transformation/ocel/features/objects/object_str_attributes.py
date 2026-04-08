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


class Parameters(Enum):
    OBJECT_STR_ATTRIBUTES = "str_obj_attr"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    One-hot-encoding of a given collection of string object attributes
    (specified inside the "str_obj_attr" parameter)

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm:
            - Parameters.OBJECT_STR_ATTRIBUTES => collection of string attributes to consider for feature extraction.

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    data = []
    feature_names = []

    ordered_objects = (
        parameters["ordered_objects"]
        if "ordered_objects" in parameters
        else ocel.objects[ocel.object_id_column].to_numpy()
    )

    object_str_attributes = exec_utils.get_param_value(
        Parameters.OBJECT_STR_ATTRIBUTES, parameters, None
    )

    if object_str_attributes is not None:
        dct_corr = {}
        dct_corr_values = {}

        for attr in object_str_attributes:
            objects_attr_not_na = (
                ocel.objects[[ocel.object_id_column, attr]]
                .dropna(subset=[attr])
                .to_dict("records")
            )
            if objects_attr_not_na:
                objects_attr_not_na = {
                    x[ocel.object_id_column]: x[attr]
                    for x in objects_attr_not_na
                }
                dct_corr[attr] = objects_attr_not_na
                dct_corr_values[attr] = list(set(objects_attr_not_na.values()))

        dct_corr_list = list(dct_corr)

        for attr in dct_corr_list:
            for value in dct_corr_values[attr]:
                feature_names.append(
                    "@@object_attr_value_" + attr + "_" + value
                )

        for ev in ordered_objects:
            data.append([0] * len(feature_names))
            count = 0
            for attr in dct_corr_list:
                if ev in dct_corr[attr]:
                    value = dct_corr[attr][ev]
                    idx = count + dct_corr_values[attr].index(value)
                    data[-1][idx] = 1.0
                count += len(dct_corr_values[attr])

    return data, feature_names
