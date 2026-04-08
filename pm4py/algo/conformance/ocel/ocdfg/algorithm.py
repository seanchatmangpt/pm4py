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


from pm4py.algo.conformance.ocel.ocdfg.variants import graph_comparison
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union
from enum import Enum
from pm4py.objects.ocel.obj import OCEL


class Variants(Enum):
    GRAPH_COMPARISON = graph_comparison


def apply(real: Union[OCEL,
                      Dict[str,
                           Any]],
          normative: Dict[str,
                          Any],
          variant=Variants.GRAPH_COMPARISON,
          parameters: Optional[Dict[Any,
                                    Any]] = None) -> Dict[str,
                                                          Any]:
    """
    Applies object-centric conformance checking between the given real object (object-centric event log or DFG)
    and a normative OC-DFG.

    Published in: https://publications.rwth-aachen.de/record/1014107

    Parameters
    -----------------
    real
        Real entity (OCEL or OC-DFG)
    normative
        Normative entity (OC-DFG)
    variant
        Variant of the algorithm to be used (default: Variants.GRAPH_COMPARISON)
    parameters
        Variant-specific parameters

    Returns
    -----------------
    conf_diagn_dict
        Dictionary with conformance diagnostics
    """
    return exec_utils.get_variant(variant).apply(real, normative, parameters)
