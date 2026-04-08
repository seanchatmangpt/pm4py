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


from typing import Union, Optional, Dict, Any
import pandas as pd
from sqlite3 import Connection as SQ3_Connection
from pm4py.objects.ocel.obj import OCEL
from pm4py.algo.querying.llm.injection.db_knowledge import (
    algorithm as db_knowledge_injector,
)
from pm4py.algo.querying.llm.injection.pm_knowledge import (
    algorithm as pm_knowledge_injection,
)


def apply(
    db: Union[pd.DataFrame, SQ3_Connection, OCEL],
    parameters: Optional[Dict[Any, Any]] = None,
) -> str:
    """
    Given a data structure containing event data, returns a string 'injecting' the required domain knowledge
    (at the database and process mining level) for LLMs purposes.

    Parameters
    ----------------
    db
        Database
    parameters
        Optional parameters

    Returns
    ----------------
    domain_knowledge
        Required domain knowledge
    """
    descr = "\n\n"
    descr += db_knowledge_injector.apply(db, parameters=parameters)
    descr += pm_knowledge_injection.apply(db, parameters=parameters)

    return descr
