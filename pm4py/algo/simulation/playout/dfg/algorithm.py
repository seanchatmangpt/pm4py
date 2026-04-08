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


from pm4py.algo.simulation.playout.dfg.variants import classic, performance
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    CLASSIC = classic
    PERFORMANCE = performance


def apply(
    dfg: Dict[Tuple[str, str], int],
    start_activities: Dict[str, int],
    end_activities: Dict[str, int],
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Union[EventLog, Dict[Tuple[str, str], int]]:
    """
    Applies the playout algorithm on a DFG, extracting the most likely traces according to the DFG

    Parameters
    ---------------
    dfg
        *Complete* DFG
    start_activities
        Start activities
    end_activities
        End activities
    variant
        Variant of the playout to be used, possible values:
        - Variants.CLASSIC
        - Variants.PERFORMANCE
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    simulated_log
        Simulated log
    """
    return exec_utils.get_variant(variant).apply(
        dfg, start_activities, end_activities, parameters=parameters
    )
