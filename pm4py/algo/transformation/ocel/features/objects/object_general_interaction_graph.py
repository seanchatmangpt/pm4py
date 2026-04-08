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
from pm4py.algo.transformation.ocel.graphs import object_interaction_graph


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object the total number of interacting object as feature

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

    g0 = object_interaction_graph.apply(ocel, parameters=parameters)
    conn = {}

    for obj in ordered_objects:
        conn[obj] = set()

    for el in g0:
        conn[el[0]].add(el[1])
        conn[el[1]].add(el[0])

    data = []
    feature_names = ["@@object_general_interaction_graph"]

    for obj in ordered_objects:
        data.append([float(len(conn[obj]))])

    return data, feature_names
