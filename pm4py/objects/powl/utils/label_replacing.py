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


from pm4py.objects.powl.obj import POWL
from typing import Optional, Dict, Any
from copy import deepcopy


def apply(powl: POWL, string_dictio: Dict[str, str], rec_depth=0, parameters: Optional[Dict[Any, Any]] = None) -> POWL:
    """
    Replaces the labels in the given POWL object using the provided dictionary.

    Parameters
    ---------------
    powl
        POWL
    string_dictio
        Correspondence dictionary (old labels -> new labels)

    Returns
    ----------------
    revised_powl
        Revised POWL
    """
    if parameters is None:
        parameters = {}

    if rec_depth == 0:
        powl = deepcopy(powl)

    if powl.label is not None and powl.label in string_dictio:
        powl.label = string_dictio[powl.label]

    for child in powl.children:
        apply(child, string_dictio, rec_depth=rec_depth+1, parameters=parameters)

    return powl
