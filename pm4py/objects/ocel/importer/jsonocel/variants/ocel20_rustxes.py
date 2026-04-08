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
from pm4py.objects.ocel.obj import OCEL
from pm4py.util.rustxes_utils import import_rustxes_backend


def apply(file_path: str, parameters: Optional[Dict[Any, Any]] = None) -> OCEL:
    """
    Imports an OCEL 2.0 JSON using the r4pm/rustxes parser.

    Parameters
    ---------------
    file_path
        Path to the OCEL 2.0 JSON
    parameters
        Optional parameters.

    Returns
    ---------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    rustxes_backend, _ = import_rustxes_backend()

    return rustxes_backend.import_ocel_json_pm4py(file_path)
