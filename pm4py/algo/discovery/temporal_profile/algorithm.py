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


from typing import Optional, Dict, Any, Union

import pandas as pd

from pm4py.algo.discovery.temporal_profile.variants import log, dataframe
from pm4py.objects.log.obj import EventLog
from pm4py.util import typing, pandas_utils


def apply(
    elog: Union[EventLog, pd.DataFrame],
    parameters: Optional[Dict[Any, Any]] = None,
) -> typing.TemporalProfile:
    """
    Discovers the temporal profile out of the provided log object.

    Implements the approach described in:
    Stertz, Florian, Jürgen Mangler, and Stefanie Rinderle-Ma. "Temporal Conformance Checking at Runtime based on Time-infused Process Models." arXiv preprint arXiv:2008.07262 (2020).

    Parameters
    ----------
    elog
        Event log
    parameters
        Parameters, including:
        - Parameters.ACTIVITY_KEY => the attribute to use as activity
        - Parameters.START_TIMESTAMP_KEY => the attribute to use as start timestamp
        - Parameters.TIMESTAMP_KEY => the attribute to use as timestamp

    Returns
    -------
    temporal_profile
        Temporal profile of the log
    """
    if pandas_utils.check_is_pandas_dataframe(elog):
        return dataframe.apply(elog, parameters=parameters)

    return log.apply(elog, parameters=parameters)
