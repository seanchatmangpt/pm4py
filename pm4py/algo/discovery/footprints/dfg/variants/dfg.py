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


from pm4py.objects.dfg import utils
from enum import Enum
from typing import Optional, Dict, Any, Tuple


class Outputs(Enum):
    DFG = "dfg"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    START_ACTIVITIES = "start_activities"
    END_ACTIVITIES = "end_activities"
    ACTIVITIES = "activities"
    SKIPPABLE = "skippable"
    ACTIVITIES_ALWAYS_HAPPENING = "activities_always_happening"
    MIN_TRACE_LENGTH = "min_trace_length"
    TRACE = "trace"


def apply(
    dfg: Dict[Tuple[str, str], int],
    parameters: Optional[Dict[Any, Any]] = None,
) -> Dict[str, Any]:
    """
    Discovers a footprint object from a DFG

    Parameters
    --------------
    dfg
        DFG
    parameters
        Parameters of the algorithm

    Returns
    --------------
    footprints_obj
        Footprints object
    """
    if parameters is None:
        parameters = {}

    parallel = {(x, y) for (x, y) in dfg if (y, x) in dfg}
    sequence = {(x, y) for (x, y) in dfg if not (y, x) in dfg}
    # replace this if needed
    start_activities = set(utils.dfg_utils.infer_start_activities(dfg))
    # replace this if needed
    end_activities = set(utils.dfg_utils.infer_end_activities(dfg))
    activities = set(utils.dfg_utils.get_activities_from_dfg(dfg))

    return {
        Outputs.SEQUENCE.value: sequence,
        Outputs.PARALLEL.value: parallel,
        Outputs.START_ACTIVITIES.value: start_activities,
        Outputs.END_ACTIVITIES.value: end_activities,
        Outputs.ACTIVITIES.value: activities,
    }
