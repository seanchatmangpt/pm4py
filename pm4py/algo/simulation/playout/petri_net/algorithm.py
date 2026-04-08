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


from pm4py.algo.simulation.playout.petri_net.variants import extensive
from pm4py.algo.simulation.playout.petri_net.variants import (
    stochastic_playout,
    basic_playout,
)
from pm4py.util import exec_utils
from enum import Enum
from pm4py.objects.petri_net.obj import PetriNet, Marking
from typing import Optional, Dict, Any
from pm4py.objects.log.obj import EventLog


class Variants(Enum):
    BASIC_PLAYOUT = basic_playout
    STOCHASTIC_PLAYOUT = stochastic_playout
    EXTENSIVE = extensive


DEFAULT_VARIANT = Variants.BASIC_PLAYOUT
VERSIONS = {
    Variants.BASIC_PLAYOUT,
    Variants.EXTENSIVE,
    Variants.STOCHASTIC_PLAYOUT,
}


def apply(
    net: PetriNet,
    initial_marking: Marking,
    final_marking: Marking = None,
    parameters: Optional[Dict[Any, Any]] = None,
    variant=DEFAULT_VARIANT,
) -> EventLog:
    """
    Do the playout of a Petrinet generating a log

    Parameters
    -----------
    net
        Petri net to play-out
    initial_marking
        Initial marking of the Petri net
    final_marking
        (if provided) Final marking of the Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm to use:

            - Variants.BASIC_PLAYOUT: selects random traces from the model, without looking at the frequency of the transitions
            - Variants.STOCHASTIC_PLAYOUT: selects random traces from the model, looking at the stochastic frequency of the transitions. Requires the provision of the stochastic map or the log.
            - Variants.EXTENSIVE: gets all the traces from the model. can be expensive

    """
    return exec_utils.get_variant(variant).apply(
        net,
        initial_marking,
        final_marking=final_marking,
        parameters=parameters,
    )
