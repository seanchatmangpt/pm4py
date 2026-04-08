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
from copy import deepcopy


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Explode an OCEL: an event associated to N objects is "split" to N events, each one associated to one object.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Possible parameters of the algorithm

    Returns
    -----------------
    ocel
        Exploded object-centric event log
    """
    if parameters is None:
        parameters = {}

    ocel = deepcopy(ocel)
    ocel.relations[ocel.event_id_column] = (
        ocel.relations[ocel.event_id_column]
        + "_"
        + ocel.relations[ocel.object_id_column]
    )
    ocel.events = ocel.relations.copy()
    del ocel.events[ocel.object_id_column]
    del ocel.events[ocel.object_type_column]

    return ocel
