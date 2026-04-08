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
from pm4py.util import pandas_utils


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Adds for each object an one-hot-encoding of the activities performed in its lifecycle

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

    activities = pandas_utils.format_unique(
        ocel.events[ocel.event_activity].unique()
    )
    lifecycle = (
        ocel.relations.groupby(ocel.object_id_column)[ocel.event_activity]
        .agg(list)
        .to_dict()
    )

    data = []
    feature_names = ["@@ocel_lif_activity_" + str(x) for x in activities]

    for obj in ordered_objects:
        data.append([])
        if obj in lifecycle:
            lif = lifecycle[obj]
        else:
            lif = []
        for act in activities:
            data[-1].append(float(len(list(x for x in lif if x == act))))

    return data, feature_names
