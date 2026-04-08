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
    Associates to each object and activity in the log the last value of the feature for a related event
    of the given activity, if exists

    Parameters
    ----------------
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

    from pm4py.algo.transformation.ocel.features.events import (
        algorithm as event_based_features,
    )

    data_events, feature_names_events = event_based_features.apply(
        ocel, parameters=parameters
    )
    dct_dct_events = event_based_features.transform_features_to_dict_dict(
        ocel, data_events, feature_names_events, parameters=parameters
    )

    ordered_objects = (
        parameters["ordered_objects"]
        if "ordered_objects" in parameters
        else ocel.objects[ocel.object_id_column].to_numpy()
    )

    stream = ocel.relations[
        [ocel.event_id_column, ocel.object_id_column, ocel.event_activity]
    ].to_dict("records")
    obj_rel_evs = {}

    for cou in stream:
        if cou[ocel.object_id_column] not in obj_rel_evs:
            obj_rel_evs[cou[ocel.object_id_column]] = []
        obj_rel_evs[cou[ocel.object_id_column]].append(
            cou[ocel.event_id_column]
        )

    ev_act = {}
    activities = set()

    for cou in stream:
        ev_act[cou[ocel.event_id_column]] = cou[ocel.event_activity]
        activities.add(cou[ocel.event_activity])

    feature_names = []
    for x in feature_names_events:
        for a in activities:
            feature_names.append("@@ev_act_fea_" + a + "_" + x)

    data = []
    for obj in ordered_objects:
        arr = []
        objs_act = {}
        if obj in obj_rel_evs:
            for ev in obj_rel_evs[obj]:
                objs_act[ev_act[ev]] = ev
        for x in feature_names_events:
            for a in activities:
                if a in objs_act:
                    val = float(dct_dct_events[objs_act[a]][x])
                else:
                    val = 0.0
                arr.append(val)
        data.append(arr)

    return data, feature_names
