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


from pm4py.algo.evaluation.generalization.variants import token_based
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    GENERALIZATION_TOKEN = token_based


GENERALIZATION_TOKEN = Variants.GENERALIZATION_TOKEN
VERSIONS = {GENERALIZATION_TOKEN}


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    petri_net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking,
    parameters: Optional[Dict[Any, Any]] = None,
    variant=GENERALIZATION_TOKEN,
) -> float:
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(
        log, petri_net, initial_marking, final_marking, parameters=parameters
    )
