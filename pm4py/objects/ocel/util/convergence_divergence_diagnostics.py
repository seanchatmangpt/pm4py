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


from pm4py.objects.ocel.util import (
    events_per_type_per_activity,
    objects_per_type_per_activity,
)
from typing import Optional, Dict, Any
from pm4py.objects.ocel.obj import OCEL


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Reports the activities and the object types for which the convergence / divergence problems occur.

    Parameters
    ----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    ret
        Dictionary with two keys ("convergence" and "divergence"). Each key is associated to a set
        of (activity, object_type) for which the specific problem occurs. An activity/object type
        which does not appear neither in the "convergence" and "divergence" section does not suffer
        of convergence and divergence problems.
    """
    if parameters is None:
        parameters = {}

    ev_per_type_per_act = events_per_type_per_activity.apply(
        ocel, parameters=parameters
    )
    obj_per_type_per_act = objects_per_type_per_activity.apply(
        ocel, parameters=parameters
    )

    ret = {"divergence": set(), "convergence": set()}

    # analyze the divergence problems
    for act in ev_per_type_per_act:
        for ot in ev_per_type_per_act[act]:
            if ev_per_type_per_act[act][ot]["median"] > 1:
                ret["divergence"].add((act, ot))

    # analyze the convergence problems
    for act in obj_per_type_per_act:
        for ot in obj_per_type_per_act[act]:
            if obj_per_type_per_act[act][ot]["median"] > 1:
                ret["convergence"].add((act, ot))

    return ret
