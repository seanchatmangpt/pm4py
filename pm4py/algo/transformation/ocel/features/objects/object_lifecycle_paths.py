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
    Adds for each object an one-hot-encoding of the paths performed in its lifecycle

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

    lifecycle = (
        ocel.relations.groupby(ocel.object_id_column)[ocel.event_activity]
        .agg(list)
        .to_dict()
    )

    data = []
    paths = {}
    all_paths = set()
    for obj in lifecycle:
        paths[obj] = []
        lobj = lifecycle[obj]
        for i in range(len(lobj) - 1):
            path = lobj[i] + "##" + lobj[i + 1]
            paths[obj].append(path)
            all_paths.add(path)

    all_paths = sorted(list(all_paths))
    feature_names = ["@@ocel_lif_path_" + str(x) for x in all_paths]

    for obj in ordered_objects:
        lif = paths[obj] if obj in paths else []
        data.append([])
        for p in all_paths:
            data[-1].append(float(len(list(x for x in lif if x == p))))

    return data, feature_names
