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


from pm4py.visualization.decisiontree.variants import classic
from pm4py.visualization.common import gview
from pm4py.visualization.common import save as gsave
from enum import Enum
from pm4py.util import exec_utils
from pm4py.visualization.common.gview import serialize, serialize_dot
from sklearn.tree import DecisionTreeClassifier
from typing import Optional, Dict, Any, List
import graphviz


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(
    clf: DecisionTreeClassifier,
    feature_names: List[str],
    classes: List[str],
    parameters: Optional[Dict[Any, Any]] = None,
    variant=DEFAULT_VARIANT,
) -> graphviz.Source:
    """
    Method to apply the visualization of the decision tree

    Parameters
    ------------
    clf
        Decision tree
    feature_names
        Names of the provided features
    classes
        Names of the target classes
    parameters
        Possible parameters of the algorithm, including:
            Parameters.FORMAT -> Image format (pdf, svg, png ...)
    variant
        Variant of the algorithm:
            - Variants.CLASSIC

    Returns
    ------------
    gviz
        GraphViz object
    """
    return exec_utils.get_variant(variant).apply(
        clf, feature_names, classes, parameters=parameters
    )


def save(gviz: graphviz.Source, output_file_path: str, parameters=None):
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


def view(gviz: graphviz.Source, parameters=None):
    """
    View the diagram

    Parameters
    -----------
    gviz
        GraphViz diagram
    """
    return gview.view(gviz, parameters=parameters)


def matplotlib_view(gviz: graphviz.Source, parameters=None):
    """
    Views the diagram using Matplotlib

    Parameters
    ---------------
    gviz
        Graphviz
    """

    return gview.matplotlib_view(gviz, parameters=parameters)
