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
from pm4py.util import exec_utils
from pm4py.algo.discovery.ilp.variants import classic
from typing import Union, Optional, Dict, Any, Tuple
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd


class Variants(Enum):
    CLASSIC = classic


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[PetriNet, Marking, Marking]:
    """
    Discovers a Petri net using the ILP miner.

    Parameters
    ---------------
    log
        Event log / Event stream / Pandas dataframe
    variant
        Variant of the algorithm to be used, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ---------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    """
    return exec_utils.get_variant(variant).apply(log, parameters)
