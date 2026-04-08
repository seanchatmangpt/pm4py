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
from typing import Optional, Dict, Any, List, Union

import pandas as pd

from pm4py.statistics.overlap.utils import compute
from pm4py.util import constants, xes_constants, exec_utils


class Parameters(Enum):
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


def apply(
    df: pd.DataFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> List[int]:
    """
    Counts the intersections of each interval event with the other interval events of the log
    (all the events are considered, not looking at the activity)

    Parameters
    ----------------
    df
        Pandas dataframe
    parameters
        Parameters of the algorithm, including:
        - Parameters.START_TIMESTAMP_KEY => the attribute to consider as start timestamp
        - Parameters.TIMESTAMP_KEY => the attribute to consider as timestamp

    Returns
    -----------------
    overlap
        For each interval event, ordered by the order of appearance in the log, associates the number
        of intersecting events.
    """
    if parameters is None:
        parameters = {}

    start_timestamp_key = exec_utils.get_param_value(
        Parameters.START_TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )
    timestamp_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY,
        parameters,
        xes_constants.DEFAULT_TIMESTAMP_KEY,
    )

    df = df[list({start_timestamp_key, timestamp_key})].to_dict("records")
    points = []

    for event in df:
        points.append(
            (
                event[start_timestamp_key].timestamp(),
                event[timestamp_key].timestamp(),
            )
        )

    return compute.apply(points)
