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


from datetime import datetime, timezone
from pm4py.util import constants


def fix_dataframe_column(serie):
    if constants.ENABLE_DATETIME_COLUMNS_AWARE:
        # Convert to UTC if the datetime is naive
        if serie.dt.tz is None:
            serie = serie.dt.tz_localize("UTC")
        else:
            # Convert to UTC if it's not already in UTC
            serie = serie.dt.tz_convert("UTC")
    else:
        serie = serie.dt.tz_localize(None)

    return serie


def fix_naivety(dt):
    if constants.ENABLE_DATETIME_COLUMNS_AWARE:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.replace(tzinfo=None)

    return dt


def apply(dt):
    """
    Parses the string to a datetime object (uses Python default strptime)

    Parameters
    --------------
    dt
        Date string

    Returns
    --------------
    datetime
        Datetime object
    """
    if dt.endswith("Z"):
        # Z at the end of date means UTC, but that is not ISO format.
        # Replace "Z" with "+00:00" that is also UTC
        dt = dt[:-1] + "+00:00"
    dt = datetime.fromisoformat(dt)

    return fix_naivety(dt)
