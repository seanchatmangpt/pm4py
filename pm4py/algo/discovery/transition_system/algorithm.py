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


from pm4py.algo.discovery.transition_system.variants import view_based
from pm4py.util import exec_utils
from enum import Enum
from pm4py.objects.transition_system.obj import TransitionSystem
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    VIEW_BASED = view_based


VERSIONS = {Variants.VIEW_BASED}
VIEW_BASED = Variants.VIEW_BASED
DEFAULT_VARIANT = Variants.VIEW_BASED


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    parameters: Optional[Dict[Any, Any]] = None,
    variant=DEFAULT_VARIANT,
) -> TransitionSystem:
    """
    Find transition system given log

    Parameters
    -----------
    log
        Log
    parameters
        Possible parameters of the algorithm, including:
            Parameters.PARAM_KEY_VIEW
            Parameters.PARAM_KEY_WINDOW
            Parameters.PARAM_KEY_DIRECTION
    variant
        Variant of the algorithm to use, including:
            Variants.VIEW_BASED

    Returns
    ----------
    ts
        Transition system
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(log, parameters=parameters)
