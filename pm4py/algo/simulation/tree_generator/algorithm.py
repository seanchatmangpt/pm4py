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


from pm4py.algo.simulation.tree_generator.variants import (
    basic,
    ptandloggenerator,
)
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.process_tree.obj import ProcessTree
from typing import Optional, Dict, Any


class Variants(Enum):
    BASIC = basic
    PTANDLOGGENERATOR = ptandloggenerator


BASIC = Variants.BASIC
PTANDLOGGENERATOR = Variants.PTANDLOGGENERATOR
DEFAULT_VARIANT = Variants.PTANDLOGGENERATOR

VERSIONS = {Variants.BASIC, Variants.PTANDLOGGENERATOR}


def apply(
    variant=DEFAULT_VARIANT, parameters: Optional[Dict[Any, Any]] = None
) -> ProcessTree:
    """
    Generate a process tree

    Parameters
    ------------
    variant
        Variant of the algorithm. Admitted values:
            - Variants.BASIC
            - Variants.PTANDLOGGENERATOR
    parameters
        Specific parameters of the algorithm

    Returns
    ------------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply(parameters=parameters)
