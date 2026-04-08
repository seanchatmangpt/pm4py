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
from typing import Any

from pm4py.algo.reduction.process_tree.variants import tree_tr_based
from pm4py.util import exec_utils


class Variants(Enum):
    TREE_TR_BASED = tree_tr_based


def apply(*args, **kwargs) -> Any:
    """
    Apply a reduction algorithm to a PM4Py object

    Parameters
    ---------------
    args
        Arguments of the reduction algorithm
    kwargs
        Keyword arguments of the reduction algorithm (including the variant, that is an item of the Variants enum)

    Returns
    ---------------
    reduced_obj
        Reduced object
    """
    variant = kwargs["variant"] if "variant" in kwargs else None
    if variant is None:
        raise Exception(
            "please specify the variant of the reduction to be used."
        )
    return exec_utils.get_variant(variant).apply(*args, **kwargs)
