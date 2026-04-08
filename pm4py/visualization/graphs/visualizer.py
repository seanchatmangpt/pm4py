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


from pm4py.visualization.graphs.variants import (
    cases,
    attributes,
    dates,
    barplot,
)
from pm4py.visualization.graphs.util.common import (
    save,
    view,
    matplotlib_view,
    serialize,
)
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, List


class Variants(Enum):
    CASES = cases
    ATTRIBUTES = attributes
    DATES = dates
    BARPLOT = barplot


DEFAULT_VARIANT = Variants.CASES


def apply(
    x: List[float],
    y: List[float],
    parameters: Optional[Dict[Any, Any]] = None,
    variant=DEFAULT_VARIANT,
) -> str:
    """
    Method to plot (non-logarithmic way) the graph with axis values contained in x and y

    Parameters
    ------------
    x
        Values for x-axis
    y
        Values for y-axis
    parameters
        Parameters of the algorithm, including:
            Parameters.FORMAT -> Format of the target image
            Parameters.TITLE -> Title of the image
    variant
        Variant of the algorithm to apply, including:
            - Variants.CASES
            - Variants.ATTRIBUTES
            - Variants.DATES
            - Variants.BARPLOT

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return exec_utils.get_variant(variant).apply_plot(
        x, y, parameters=parameters
    )


def apply_plot(
    x: List[float],
    y: List[float],
    parameters: Optional[Dict[Any, Any]] = None,
    variant=DEFAULT_VARIANT,
) -> str:
    """
    Method to plot (non-logarithmic way) the graph with axis values contained in x and y

    Parameters
    ------------
    x
        Values for x-axis
    y
        Values for y-axis
    parameters
        Parameters of the algorithm, including:
            Parameters.FORMAT -> Format of the target image
            Parameters.TITLE -> Title of the image
    variant
        Variant of the algorithm to apply, including:
            - Variants.CASES
            - Variants.ATTRIBUTES
            - Variants.DATES
            - Variants.BARPLOT

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return exec_utils.get_variant(variant).apply_plot(
        x, y, parameters=parameters
    )


def apply_semilogx(
    x: List[float],
    y: List[float],
    parameters: Optional[Dict[Any, Any]] = None,
    variant=DEFAULT_VARIANT,
) -> str:
    """
    Method to plot (semi-logarithmic way) the graph with axis values contained in x and y

    Parameters
    ------------
    x
        Values for x-axis
    y
        Values for y-axis
    parameters
        Parameters of the algorithm, including:
            Parameters.FORMAT -> Format of the target image
            Parameters.TITLE -> Title of the image
    variant
        Variant of the algorithm to apply, including:
            - Variants.CASES
            - Variants.ATTRIBUTES
            - Variants.DATES
            - Variants.BARPLOT

    Returns
    ------------
    temp_file_name
        Representation temporary file name
    """
    return exec_utils.get_variant(variant).apply_semilogx(
        x, y, parameters=parameters
    )
