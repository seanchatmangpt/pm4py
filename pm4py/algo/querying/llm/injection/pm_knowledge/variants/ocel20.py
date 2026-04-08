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


import pandas as pd
from typing import Optional, Dict, Any, Union
from pm4py.objects.ocel.obj import OCEL


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None) -> str:
    """
    Provides a string containing the required process mining domain knowledge for object-centric process mining structures
    (in order for the LLM to produce meaningful queries).

    Parameters
    ---------------
    ocel
        OCEL (2.0) object
    parameters
        Optional parameters of the method

    Returns
    --------------
    pm_knowledge
        String containing the required process mining knowledge
    """
    if parameters is None:
        parameters = {}

    descr = """
If you need to compute the duration of a lifecycle of an object, compute the difference between the timestamp of the last and the first event of the lifecycle.
If you need to compute the variant for an object, aggregate the names of the activities.
    """

    return descr
