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


from pm4py.algo.discovery.causal.variants import alpha, heuristic
from enum import Enum
from pm4py.util import exec_utils
from typing import Dict, Tuple


class Variants(Enum):
    CAUSAL_ALPHA = alpha
    CAUSAL_HEURISTIC = heuristic


CAUSAL_ALPHA = Variants.CAUSAL_ALPHA
CAUSAL_HEURISTIC = Variants.CAUSAL_HEURISTIC

VERSIONS = {CAUSAL_ALPHA, CAUSAL_HEURISTIC}


def apply(
    dfg: Dict[Tuple[str, str], int], variant=CAUSAL_ALPHA
) -> Dict[Tuple[str, str], int]:
    """
    Computes the causal relation on the basis of a given directly follows graph.

    Parameters
    -----------
    dfg
        Directly follows graph
    variant
        Variant of the algorithm to use:
            - Variants.CAUSAL_ALPHA
            - Variants.CAUSAL_HEURISTIC

    Returns
    -----------
    causal relations
        dict
    """
    return exec_utils.get_variant(variant).apply(dfg)
