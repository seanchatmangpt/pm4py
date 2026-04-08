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
    Feature: assigns to each event the number of related objects.

    Parameters
    ----------------
    ocel
        OCEL
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    ordered_events = (
        parameters["ordered_events"]
        if "ordered_events" in parameters
        else ocel.events[ocel.event_id_column].to_numpy()
    )

    rel_objs = (
        ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column]
        .agg(list)
        .to_dict()
    )

    data = []
    feature_names = ["@@event_num_rel_objs"]

    for ev in ordered_events:
        data.append([float(len(rel_objs[ev]))])

    return data, feature_names
