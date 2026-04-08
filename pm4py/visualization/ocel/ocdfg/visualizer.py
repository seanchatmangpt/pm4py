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
from pm4py.visualization.ocel.ocdfg.variants import classic, elkjs
from typing import Optional, Dict, Any


class Variants(Enum):
    CLASSIC = classic
    ELKJS = elkjs


def apply(
    ocdfg: Dict[str, Any],
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Digraph:
    """
    Visualizes an OC-DFG using one of the provided visualizations.

    Parameters
    ----------------
    ocdfg
        Object-centric directly-follows graph
    variant
        Available variants. Possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ----------------
    viz
        Graphviz DiGraph
    """
    return exec_utils.get_variant(variant).apply(ocdfg, parameters)


def save(
    gviz, output_file_path: str, variant=Variants.CLASSIC, parameters=None
):
    """
    Saves the diagram
    """
    return exec_utils.get_variant(variant).save(
        gviz, output_file_path, parameters
    )


def view(gviz, variant=Variants.CLASSIC, parameters=None):
    """
    Views the diagram
    """
    return exec_utils.get_variant(variant).view(gviz, parameters)


def matplotlib_view(gviz, variant=Variants.CLASSIC, parameters=None):
    """
    Views the diagram using Matplotlib
    """
    return exec_utils.get_variant(variant).matplotlib_view(gviz, parameters)
