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


from pm4py.visualization.bpmn.variants import classic, dagrejs, bpmnio_auto_layout
from pm4py.util import exec_utils
from enum import Enum
from pm4py.visualization.common.gview import serialize, serialize_dot
from typing import Optional, Dict, Any
from pm4py.objects.bpmn.obj import BPMN
import graphviz


class Variants(Enum):
    CLASSIC = classic
    DAGREJS = dagrejs
    BPMNIO_AUTO_LAYOUT = bpmnio_auto_layout


DEFAULT_VARIANT = Variants.CLASSIC


def apply(
    bpmn_graph: BPMN,
    variant=DEFAULT_VARIANT,
    parameters: Optional[Dict[Any, Any]] = None,
) -> graphviz.Digraph:
    """
    Visualize a BPMN graph

    Parameters
    -------------
    bpmn_graph
        BPMN graph
    variant
        Variant of the visualization, possible values:
         - Variants.CLASSIC
    parameters
        Version-specific parameters

    Returns
    ------------
    gviz
        Graphviz representation
    """
    return exec_utils.get_variant(variant).apply(
        bpmn_graph, parameters=parameters
    )


def save(
    gviz: graphviz.Digraph,
    output_file_path: str,
    variant=DEFAULT_VARIANT,
    parameters=None,
):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    return exec_utils.get_variant(variant).save(
        gviz, output_file_path, parameters=parameters
    )


def view(gviz: graphviz.Digraph, variant=DEFAULT_VARIANT, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return exec_utils.get_variant(variant).view(gviz, parameters=parameters)


def matplotlib_view(
    gviz: graphviz.Digraph, variant=DEFAULT_VARIANT, parameters=None
):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """
    return exec_utils.get_variant(variant).matplotlib_view(
        gviz, parameters=parameters
    )
