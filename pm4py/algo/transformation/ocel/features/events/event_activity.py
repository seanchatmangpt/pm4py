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
    One-hot encode the activities of an OCEL, assigning to each event its own activity as feature

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

    activities = pandas_utils.format_unique(
        ocel.events[ocel.event_activity].unique()
    )

    data = []
    feature_names = ["@@event_act_" + act for act in activities]

    events_activities = ocel.events[
        [ocel.event_id_column, ocel.event_activity]
    ].to_dict("records")
    events_activities = {
        x[ocel.event_id_column]: x[ocel.event_activity]
        for x in events_activities
    }

    for ev in ordered_events:
        data.append([0.0] * len(activities))
        data[-1][activities.index(events_activities[ev])] = 1.0

    return data, feature_names
