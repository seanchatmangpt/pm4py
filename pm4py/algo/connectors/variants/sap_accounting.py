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



from typing import Optional, Dict, Any
from enum import Enum
from pm4py.util import exec_utils, pandas_utils
import pandas as pd


class Parameters(Enum):
    CONNECTION_STRING = "connection_string"
    PREFIX = "prefix"


def apply(conn, parameters: Optional[Dict[Any, Any]] = None) -> pd.DataFrame:
    """
    Extracts an event log for the SAP Accounting process

    Parameters
    ---------------
    conn
        (if provided) ODBC connection object to the database (offering cursors)
    parameters
        Parameters of the algorithm, including:
        - Parameters.CONNECTION_STRING => connection string that is used (if no connection is provided)
        - Parameters.PREFIX => prefix to add to the table names (example SAPSR3.)

    Returns
    ---------------
    dataframe
        Pandas dataframe
    """
    if parameters is None:
        parameters = {}

    import pm4py

    connection_string = exec_utils.get_param_value(
        Parameters.CONNECTION_STRING, parameters, None
    )

    if conn is None:
        import pyodbc

        conn = pyodbc.connect(connection_string)

    prefix = exec_utils.get_param_value(Parameters.PREFIX, parameters, "")

    curs = conn.cursor()

    query = (
        """
    SELECT * FROM
    (SELECT MANDT || '-' || BUKRS || '-' || GJAHR || '-' || BELNR AS "case:concept:name", 'Create Financial Document - ' || BLART AS "concept:name", CPUDT || ' ' || CPUTM AS "time:timestamp", USNAM AS "org:resource", BLART FROM """
        + prefix
        + """BKPF
    UNION
    SELECT MANDT || '-' || BUKRS || '-' || GJAHR || '-' || AUGBL AS "case:concept:name", 'Clear Customer Document' AS "concept:name", AUGDT || ' 235958' AS "time:timestamp", NULL AS "org:resource", NULL AS BLART FROM """
        + prefix
        + """BSAD
    UNION
    SELECT MANDT || '-' || BUKRS || '-' || GJAHR || '-' || AUGBL AS "case:concept:name", 'Clear Vendor Document' AS "concept:name", AUGDT || ' 235959' AS "time:timestamp", NULL AS "org:resource", NULL AS BLART FROM """
        + prefix
        + """BSAK)
    ORDER BY "case:concept:name", "time:timestamp";
    """
    )
    columns = [
        "case:concept:name",
        "concept:name",
        "time:timestamp",
        "org:resource",
        "BLART",
    ]

    curs.execute(query)
    dataframe = curs.fetchall()
    dataframe = pandas_utils.instantiate_dataframe_from_records(
        dataframe, columns=columns
    )
    dataframe = pm4py.format_dataframe(dataframe)

    curs.close()
    conn.close()

    return dataframe
