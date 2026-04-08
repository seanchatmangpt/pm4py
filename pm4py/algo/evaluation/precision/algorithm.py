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


from pm4py.algo.evaluation.precision.variants import etconformance_token
from pm4py.algo.evaluation.precision.variants import align_etconformance
from pm4py.algo.evaluation.precision.variants import automaton_after_align
from pm4py.objects.petri_net.utils.check_soundness import (
    check_easy_soundness_net_in_fin_marking,
)
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.objects.petri_net.obj import PetriNet, Marking
import pandas as pd


class Variants(Enum):
    ETCONFORMANCE_TOKEN = etconformance_token
    ALIGN_ETCONFORMANCE = align_etconformance
    AUTOMATON_AFTER_ALIGN = automaton_after_align


ETCONFORMANCE_TOKEN = Variants.ETCONFORMANCE_TOKEN
ALIGN_ETCONFORMANCE = Variants.ALIGN_ETCONFORMANCE
AUTOMATON_AFTER_ALIGN = Variants.AUTOMATON_AFTER_ALIGN

VERSIONS = {ETCONFORMANCE_TOKEN, ALIGN_ETCONFORMANCE}


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    net: PetriNet,
    marking: Marking,
    final_marking: Marking,
    parameters: Optional[Dict[Any, Any]] = None,
    variant=None,
) -> float:
    """
    Method to apply ET Conformance

    Parameters
    -----------
    log
        Trace log
    net
        Petri net
    marking
        Initial marking
    final_marking
        Final marking
    parameters
        Parameters of the algorithm, including:
            pm4py.util.constants.PARAMETER_CONSTANT_ACTIVITY_KEY -> Activity key
    variant
        Variant of the algorithm that should be applied:
            - Variants.ETCONFORMANCE_TOKEN
            - Variants.ALIGN_ETCONFORMANCE
    """
    if parameters is None:
        parameters = {}

    # execute the following part of code when the variant is not specified by
    # the user
    if variant is None:
        if not (
            check_easy_soundness_net_in_fin_marking(
                net, marking, final_marking
            )
        ):
            # in the case the net is not a easy sound workflow net, we must
            # apply token-based replay
            variant = ETCONFORMANCE_TOKEN
        else:
            # otherwise, use the align-etconformance approach (safer, in the
            # case the model contains duplicates)
            variant = ALIGN_ETCONFORMANCE

    return exec_utils.get_variant(variant).apply(
        log, net, marking, final_marking, parameters=parameters
    )
