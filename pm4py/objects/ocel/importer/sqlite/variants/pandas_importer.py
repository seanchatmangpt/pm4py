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
from typing import Dict, Any, Optional
import pandas as pd
from pm4py.objects.ocel.util import ocel_consistency
from pm4py.objects.ocel.util import filtering_utils
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import pandas_utils, constants as pm4_constants


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an OCEL from a SQLite database using Pandas

    Parameters
    --------------
    file_path
        Path to the SQLite database
    parameters
        Parameters of the import

    Returns
    --------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    import sqlite3

    conn = sqlite3.connect(file_path)

    events = pd.read_sql("SELECT * FROM EVENTS", conn)
    objects = pd.read_sql("SELECT * FROM OBJECTS", conn)
    relations = pd.read_sql("SELECT * FROM RELATIONS", conn)

    events = dataframe_utils.convert_timestamp_columns_in_df(
        events,
        timest_format=pm4_constants.DEFAULT_TIMESTAMP_PARSE_FORMAT,
        timest_columns=["ocel:timestamp"],
    )

    relations = dataframe_utils.convert_timestamp_columns_in_df(
        relations,
        timest_format=pm4_constants.DEFAULT_TIMESTAMP_PARSE_FORMAT,
        timest_columns=["ocel:timestamp"],
    )

    ocel = OCEL(
        events=events,
        objects=objects,
        relations=relations,
        parameters=parameters,
    )
    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(
        ocel, parameters=parameters
    )

    return ocel
