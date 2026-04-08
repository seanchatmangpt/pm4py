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


from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from enum import Enum
from pm4py.visualization.network_analysis.variants import (
    frequency,
    performance,
)
from pm4py.util import exec_utils
from graphviz import Digraph
from typing import Dict, Optional, Any, Tuple


class Variants(Enum):
    FREQUENCY = frequency
    PERFORMANCE = performance


def apply(
    network_analysis_edges: Dict[Tuple[str, str], Dict[str, Any]],
    variant=Variants.FREQUENCY,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Digraph:
    """
    Creates a visualization of the network analysis

    Parameters
    ----------------
    network_analysis_edges
        Edges of the network analysis
    parameters
        Version-specific parameters

    Returns
    ----------------
    digraph
        Graphviz graph
    """
    return exec_utils.get_variant(variant).apply(
        network_analysis_edges, parameters=parameters
    )


def save(gviz: Digraph, output_file_path: str, parameters=None):
    """
    Save the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    output_file_path
        Path where the GraphViz output should be saved
    """
    gsave.save(gviz, output_file_path, parameters=parameters)
    return ""


def view(gviz: Digraph, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: Digraph, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)
