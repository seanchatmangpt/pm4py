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


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the number of events in its lifecycle as feature

    Parameters
    -----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    data
        Values of the added features
    feature_names
        Names of the added features
    """
    if parameters is None:
        parameters = {}

    ordered_objects = (
        parameters["ordered_objects"]
        if "ordered_objects" in parameters
        else ocel.objects[ocel.object_id_column].to_numpy()
    )

    lifecycle_length = (
        ocel.relations.groupby(ocel.object_id_column).size().to_dict()
    )

    data = []
    feature_names = ["@@object_lifecycle_length"]

    for obj in ordered_objects:
        if obj in lifecycle_length:
            data.append([float(lifecycle_length[obj])])
        else:
            data.append([0.0])

    return data, feature_names
