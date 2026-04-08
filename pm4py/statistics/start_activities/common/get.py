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


def get_sorted_start_activities_list(start_activities):
    """
    Gets sorted start attributes list

    Parameters
    ----------
    start_activities
        Dictionary of start attributes associated with their count

    Returns
    ----------
    listact
        Sorted start attributes list
    """
    listact = []
    for sa in start_activities:
        listact.append([sa, start_activities[sa]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact


def get_start_activities_threshold(salist, decreasing_factor):
    """
    Get start attributes cutting threshold

    Parameters
    ----------
    salist
        Sorted start attributes list
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        Start attributes cutting threshold
    """
    threshold = salist[0][1]
    for i in range(1, len(salist)):
        value = salist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold
