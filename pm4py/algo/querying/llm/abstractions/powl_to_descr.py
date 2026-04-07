'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

from enum import Enum
from typing import Optional, Dict, Any
from pm4py.objects.powl.obj import POWL
from pm4py.util import exec_utils
from pm4py.util import constants


class Parameters(Enum):
    RESPONSE_HEADER = "response_header"
    MAX_LEN = "max_len"


def apply(
    powl: POWL,
    parameters: Optional[Dict[Any, Any]] = None,
) -> str:
    """
    Provides the description of a POWL (Partially Ordered Workflow Language) model.

    Parameters
    --------------
    powl
        POWL model
    parameters
        Possible parameters of the algorithm, including:
        - Parameters.RESPONSE_HEADER => includes the header explaining POWL semantics
        - Parameters.MAX_LEN => maximum length of the returned string

    Returns
    --------------
    stru
        String representation of the given POWL model
    """
    if parameters is None:
        parameters = {}

    include_header = exec_utils.get_param_value(
        Parameters.RESPONSE_HEADER, parameters, True
    )
    max_len = exec_utils.get_param_value(
        Parameters.MAX_LEN, parameters, constants.OPENAI_MAX_LEN
    )

    ret = ["\n"]
    if include_header:
        ret.append(POWL.model_description())
        ret.append("The following POWL model was discovered:\n")
    ret.append(repr(powl))
    ret.append("\n")

    result = "\n".join(ret)
    return result[:max_len]
