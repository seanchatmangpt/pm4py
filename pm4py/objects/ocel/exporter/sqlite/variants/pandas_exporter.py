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
from pm4py.objects.ocel.util import ocel_consistency
from pm4py.objects.ocel.util import filtering_utils
import os


def apply(
    ocel: OCEL, target_path: str, parameters: Optional[Dict[Any, Any]] = None
):
    """
    Exports an OCEL to a SQLite database using Pandas

    Parameters
    ---------------
    ocel
        Object-centric event log
    target_path
        Path to the SQLite database
    parameters
        Parameters of the exporter
    """
    if parameters is None:
        parameters = {}

    import sqlite3

    if os.path.exists(target_path):
        os.remove(target_path)

    ocel = ocel_consistency.apply(ocel, parameters=parameters)
    ocel = filtering_utils.propagate_relations_filtering(
        ocel, parameters=parameters
    )

    conn = sqlite3.connect(target_path)

    ocel.events.to_sql("EVENTS", conn, index=False)
    ocel.relations.to_sql("RELATIONS", conn, index=False)
    ocel.objects.to_sql("OBJECTS", conn, index=False)

    conn.close()
