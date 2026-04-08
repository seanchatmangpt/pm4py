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

from pm4py.objects.bpmn.layout.variants import graphviz, graphviz_new
from pm4py.util import exec_utils


class Variants(Enum):
    GRAPHVIZ = graphviz
    GRAPHVIZ_NEW = graphviz_new


DEFAULT_VARIANT = Variants.GRAPHVIZ_NEW


def apply(bpmn_graph, variant=DEFAULT_VARIANT, parameters=None):
    """
    Layouts a BPMN graph (inserting the positions of the nodes and the layouting of the edges)

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    variant
        Variant of the algorithm to use, possible values:
        - Variants.GRAPHVIZ
    parameters
        Parameters of the algorithm

    Returns
    -------------
    bpmn_graph
        BPMN graph with layout information
    """
    return exec_utils.get_variant(variant).apply(
        bpmn_graph, parameters=parameters
    )
