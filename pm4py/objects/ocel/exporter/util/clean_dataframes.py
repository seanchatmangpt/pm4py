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


from typing import Optional, Dict, Any, Tuple
import datetime as dt

import numpy as np
import pandas as pd

from pm4py.objects.ocel.obj import OCEL


def is_null(value) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, dict, tuple, set)):
        return False
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def normalize_value(value):
    if is_null(value):
        return None
    if isinstance(value, (list, dict, tuple, set)):
        return value
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, np.datetime64):
        return pd.to_datetime(value).isoformat()
    if isinstance(value, np.timedelta64):
        return str(pd.to_timedelta(value))
    if isinstance(value, np.generic):
        return value.item()
    return value


def get_dataframes_from_ocel(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if parameters is None:
        parameters = {}

    events = ocel.events.copy()
    for col in events.columns:
        if str(events[col].dtype) == "object":
            events[col] = events[col].map(normalize_value)
        elif "date" in str(events[col].dtype):
            events[col] = events[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    objects = ocel.objects.copy()
    for col in objects.columns:
        if str(objects[col].dtype) == "object":
            objects[col] = objects[col].map(normalize_value)
        elif "date" in str(objects[col].dtype):
            objects[col] = objects[col].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    return events, objects
