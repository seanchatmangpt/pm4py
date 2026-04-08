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


from pm4py.visualization.transition_system.util import visualize_graphviz
from enum import Enum
from typing import Optional, Dict, Any, Union
from pm4py.objects.transition_system.obj import TransitionSystem
import graphviz


class Parameters(Enum):
    FORMAT = "format"
    SHOW_LABELS = "show_labels"
    SHOW_NAMES = "show_names"
    FORCE_NAMES = "force_names"
    FILLCOLORS = "fillcolors"
    FONT_SIZE = "font_size"
    ENABLE_GRAPH_TITLE = "enable_graph_title"
    GRAPH_TITLE = "graph_title"


def apply(
    tsys: TransitionSystem,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> graphviz.Digraph:
    """
    Get visualization of a Transition System

    Parameters
    -----------
    tsys
        Transition system
    parameters
        Optional parameters of the algorithm

    Returns
    ----------
    gviz
        Graph visualization
    """

    gviz = visualize_graphviz.visualize(tsys, parameters=parameters)
    return gviz
