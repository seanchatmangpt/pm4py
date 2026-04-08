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


def pick_chosen_points(m, n):
    """
    Pick chosen points in a list

    Parameters
    ------------
    m
        Number of wanted points
    n
        Number of current points

    Returns
    ------------
    indexes
        Indexes of chosen points
    """
    return [i * n // m + n // (2 * m) for i in range(m)]


def pick_chosen_points_list(m, lst, include_extremes=True):
    """
    Pick a chosen number of points from a list

    Parameters
    -------------
    m
        Number of wanted points
    lst
        List

    Returns
    -------------
    reduced_lst
        Reduced list
    """
    n = len(lst)
    points = pick_chosen_points(m, n)

    if include_extremes:
        if 0 not in points:
            points = [0] + points

        if len(lst)-1 not in points:
            points = points + [len(lst)-1]

    ret = []
    for i in points:
        ret.append(lst[i])

    return ret
