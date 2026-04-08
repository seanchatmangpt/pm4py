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


from graphviz import Digraph
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.ocel.ocpn.variants import wo_decoration, brachmann
from typing import Optional, Dict, Any
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave


class Variants(Enum):
    WO_DECORATION = wo_decoration
    BRACHMANN = brachmann


def apply(
    ocpn: Dict[str, Any],
    variant=Variants.WO_DECORATION,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Digraph:
    """
    Obtains a visualization of the provided object-centric Petri net

    Reference paper: van der Aalst, Wil MP, and Alessandro Berti. "Discovering object-centric Petri nets." Fundamenta informaticae 175.1-4 (2020): 1-40.

    Parameters
    ----------------
    ocpn
        Object-centric Petri net
    variant
        Variant of the algorithm to be used
    parameters
        Variant-specific parameters

    Returns
    ---------------
    gviz
        Graphviz digraph
    """
    return exec_utils.get_variant(variant).apply(ocpn, parameters=parameters)


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
