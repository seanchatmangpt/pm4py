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
from pm4py.objects.petri_net.obj import PetriNet, Marking
from enum import Enum
from pm4py.util import exec_utils


class Parameters(Enum):
    RESPONSE_HEADER = "response_header"


def apply(
    net: PetriNet,
    im: Marking,
    fm: Marking,
    parameters: Optional[Dict[Any, Any]] = None,
) -> str:
    """
    Provides the description of an accepting Petri net

    Parameters
    --------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.INCLUDE_HEADER => includes the header

    Returns
    --------------
    stru
        String representation of the given accepting Petri net
    """
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(
        Parameters.RESPONSE_HEADER, parameters, True
    )

    ret = ["\n"]
    if include_header:
        ret.append("If I have a Petri net:\n")
    ret.append(repr(net))
    ret.append("\ninitial marking: " + repr(im))
    ret.append("final marking: " + repr(fm))
    ret.append("\n")

    return "\n".join(ret)
