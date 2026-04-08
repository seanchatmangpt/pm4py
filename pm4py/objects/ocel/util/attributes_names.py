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


from typing import Optional, Dict, Any, List

from pm4py.objects.ocel import constants
from pm4py.objects.ocel.obj import OCEL


def get_attribute_names(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> List[str]:
    """
    Gets the list of attributes at the event and the object level of an object-centric event log
    (e.g. ["cost", "amount", "name"])

    Parameters
    -------------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    -------------------
    attributes_list
        List of attributes at the event and object level (e.g. ["cost", "amount", "name"])
    """
    if parameters is None:
        parameters = {}

    attributes = sorted(
        set(
            x
            for x in ocel.events.columns
            if not x.startswith(constants.OCEL_PREFIX)
        ).union(
            x
            for x in ocel.objects.columns
            if not x.startswith(constants.OCEL_PREFIX)
        )
    )

    return attributes
