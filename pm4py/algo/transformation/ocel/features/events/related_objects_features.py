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
    Extracts for each event the minimum and the maximum value of the features for the objects related to the event.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters

    Returns
    -----------------
    data
        Extracted feature values
    feature_names
        Feature names
    """
    if parameters is None:
        parameters = {}

    from pm4py.algo.transformation.ocel.features.objects import (
        algorithm as object_based_features,
    )

    data_objects, feature_names_objects = object_based_features.apply(
        ocel, parameters=parameters
    )
    dct_dct_objects = object_based_features.transform_features_to_dict_dict(
        ocel, data_objects, feature_names_objects, parameters=parameters
    )

    ordered_events = (
        parameters["ordered_events"]
        if "ordered_events" in parameters
        else ocel.events[ocel.event_id_column].to_numpy()
    )

    stream = ocel.relations[
        [ocel.event_id_column, ocel.object_id_column]
    ].to_dict("records")
    ev_rel_objs = {}

    for cou in stream:
        if cou[ocel.event_id_column] not in ev_rel_objs:
            ev_rel_objs[cou[ocel.event_id_column]] = []
        ev_rel_objs[cou[ocel.event_id_column]].append(
            dct_dct_objects[cou[ocel.object_id_column]]
        )

    data = []
    feature_names = []
    for x in feature_names_objects:
        feature_names.append("@@rel_obj_fea_min_" + x)
        feature_names.append("@@rel_obj_fea_max_" + x)

    for ev in ordered_events:
        arr = []
        for x in feature_names_objects:
            if ev in ev_rel_objs:
                min_v = float(min(y[x] for y in ev_rel_objs[ev]))
                max_v = float(max(y[x] for y in ev_rel_objs[ev]))
            else:
                min_v = 0.0
                max_v = 0.0
            arr.append(min_v)
            arr.append(max_v)
        data.append(arr)

    return data, feature_names
