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



from enum import Enum

from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL
from pm4py.util import constants
from typing import Optional, Dict, Any, Union, Tuple


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY
    START_TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_START_TIMESTAMP_KEY
    KEEP_FIRST_FOLLOWING = "keep_first_following"


def apply(
    interval_log: IMDataStructureUVCL,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[Tuple[str, str], int]:
    if parameters is None:
        parameters = {}

    ret_dict = {}
    for trace, freq in interval_log.data_structure.items():
        i = 0
        while i < len(trace):
            act1 = trace[i]
            j = i + 1
            while j < len(trace):
                act2 = trace[j]
                tup = (act1, act2)
                if tup in ret_dict.keys():
                    ret_dict[tup] = ret_dict[tup] + freq
                else:
                    ret_dict[tup] = freq
                j = j + 1
            i = i + 1

    return ret_dict
