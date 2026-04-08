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
from typing import Optional, Dict, Any, Tuple, List, Union

from pm4py.util.intervaltree import Interval, IntervalTree

from pm4py.util import exec_utils


class Parameters(Enum):
    EPSILON = "epsilon"


def apply(
    points: List[Tuple[float, float]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> List[int]:
    """
    Computes the overlap statistic given a list of points, expressed as (min_timestamp, max_timestamp)

    Parameters
    -----------------
    points
        List of points with the aforementioned features
    parameters
        Parameters of the method, including:
        - Parameters.EPSILON

    Returns
    -----------------
    overlap
        List associating to each point the number of intersecting points
    """
    if parameters is None:
        parameters = {}

    epsilon = exec_utils.get_param_value(
        Parameters.EPSILON, parameters, 10 ** (-5)
    )
    points = [(x[0] - epsilon, x[1] + epsilon) for x in points]
    sorted_points = sorted(points)
    tree = IntervalTree()

    for p in sorted_points:
        tree.add(Interval(p[0], p[1]))

    overlap = []
    for p in points:
        overlap.append(len(tree[p[0]: p[1]]))

    return overlap
