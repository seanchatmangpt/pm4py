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
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Union, Tuple, Set
from pm4py.algo.conformance.ocel.etot.variants import graph_comparison


class Variants(Enum):
    GRAPH_COMPARISON = graph_comparison


def apply(real: Union[OCEL,
                      Tuple[Set[str],
                            Set[str],
                            Set[Tuple[str,
                                      str]],
                            Dict[Tuple[str,
                                       str],
                                 int]]],
          normative: Tuple[Set[str],
                           Set[str],
                           Set[Tuple[str,
                                     str]],
                           Dict[Tuple[str,
                                      str],
                                int]],
          variant=Variants.GRAPH_COMPARISON,
          parameters: Optional[Dict[Any,
                                    Any]] = None) -> Dict[str,
                                                          Any]:
    """
    Applies ET-OT-based conformance checking between a 'real' object (either an OCEL or an ET-OT graph),
    and a normative ET-OT graph.

    Published in: https://publications.rwth-aachen.de/record/1014107

    Parameters
    -------------------
    real
        Real object (OCEL, or ET-OT graph)
    normative
        Normative object (ET-OT graph)
    variant
        Variant of the algorithm to be used:
        - Variants.GRAPH_COMPARISON
    parameters
        Variant-specific parameters.

    Returns
    ------------------
    diagn_dict
        Diagnostics dictionary
    """
    return exec_utils.get_variant(variant).apply(real, normative, parameters)
