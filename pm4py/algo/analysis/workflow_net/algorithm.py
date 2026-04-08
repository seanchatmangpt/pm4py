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

from pm4py.algo.analysis.workflow_net.variants import petri_net
from pm4py.util import exec_utils
from typing import Optional, Dict, Any
from pm4py.objects.petri_net.obj import PetriNet


class Variants(Enum):
    PETRI_NET = petri_net


def apply(
    net: PetriNet,
    parameters: Optional[Dict[Any, Any]] = None,
    variant=Variants.PETRI_NET,
) -> bool:
    """
    Checks if a Petri net is a workflow net

    Parameters
    ---------------
    net
        Petri net
    parameters
        Parameters of the algorithm
    variant
        Variant of the algorithm, possibe values:
        - Variants.PETRI_NET

    Returns
    ---------------
    boolean
        Boolean value
    """
    return exec_utils.get_variant(variant).apply(net, parameters=parameters)
