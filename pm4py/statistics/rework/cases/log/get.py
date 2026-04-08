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


from enum import Enum
from typing import Optional, Dict, Any, Union

from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(
    log: EventLog,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[str, Dict[str, int]]:
    """
    Computes for each trace of the event log how much rework occurs.
    The rework is computed as the difference between the total number of activities of a trace and the
    number of unique activities.

    Parameters
    ----------------
    log
        Event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.CASE_ID_KEY => the case identifier attribute

    Returns
    -----------------
    dict
        Dictionary associating to each case ID:
        - The number of total activities of the case (number of events)
        - The rework (difference between the total number of activities of a trace and the number of unique activities)
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, xes_constants.DEFAULT_TRACEID_KEY
    )

    rework_cases = {}
    for trace in log:
        activities = list([x[activity_key] for x in trace])
        unique_activities = set(activities)
        rework = len(activities) - len(unique_activities)
        rework_cases[trace.attributes[case_id_key]] = {
            "number_activities": len(activities),
            "rework": rework,
        }

    return rework_cases
