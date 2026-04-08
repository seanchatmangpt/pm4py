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



from pm4py.objects.conversion.powl.variants import to_petri_net
from pm4py.objects.conversion.powl.variants import to_bpmn
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    TO_PETRI_NET = to_petri_net
    TO_BPMN = to_bpmn


def apply(powl, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Method for converting from POWL to other process model formats.

    Parameters
    -----------
    powl
        POWL model
    parameters
        Parameters of the algorithm
    variant
        Chosen variant of the algorithm:
            - Variants.TO_PETRI_NET: converts to a Petri net
            - Variants.TO_BPMN: converts to a BPMN model (requires 'powl' package)

    Returns
    -----------
    For TO_PETRI_NET:
        net: Petri net
        initial_marking: Initial marking
        final_marking: Final marking
    For TO_BPMN:
        bpmn_graph: BPMN model
    """
    return exec_utils.get_variant(variant).apply(powl, parameters=parameters)
