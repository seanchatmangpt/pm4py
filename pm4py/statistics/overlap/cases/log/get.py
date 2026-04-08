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
from typing import Dict, Optional, Any, List, Union

from pm4py.objects.log.obj import EventLog
from pm4py.statistics.overlap.utils import compute
from pm4py.util import exec_utils, constants, xes_constants
from pm4py.objects.conversion.log import converter


class Parameters(Enum):
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY


def apply(
    log: EventLog,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> List[int]:
    """
    Computes the case overlap statistic from an interval event log

    Parameters
    -----------------
    log
        Interval event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.TIMESTAMP_KEY => attribute representing the completion timestamp
        - Parameters.START_TIMESTAMP_KEY => attribute representing the start timestamp

    Returns
    ----------------
    case overlap
        List associating to each case the number of open cases during the life of a case
    """
    if parameters is None:
        parameters = {}

    log = converter.apply(
        log, variant=converter.Variants.TO_EVENT_LOG, parameters=parameters
    )

    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )

    points = []
    for trace in log:
        case_points = []
        for event in trace:
            case_points.append(
                (
                    event[start_timestamp_key].timestamp(),
                    event[timestamp_key].timestamp(),
                )
            )
        points.append(
            (min(x[0] for x in case_points), max(x[1] for x in case_points))
        )

    return compute.apply(points, parameters=parameters)
