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


def get_sorted_end_activities_list(end_activities):
    """
    Gets sorted end attributes list

    Parameters
    ----------
    end_activities
        Dictionary of end attributes associated with their count

    Returns
    ----------
    listact
        Sorted end attributes list
    """
    listact = []
    for ea in end_activities:
        listact.append([ea, end_activities[ea]])
    listact = sorted(listact, key=lambda x: x[1], reverse=True)
    return listact


def get_end_activities_threshold(ealist, decreasing_factor):
    """
    Get end attributes cutting threshold

    Parameters
    ----------
    ealist
        Sorted end attributes list
    decreasing_factor
        Decreasing factor of the algorithm

    Returns
    ---------
    threshold
        End attributes cutting threshold
    """

    threshold = ealist[0][1]
    for i in range(1, len(ealist)):
        value = ealist[i][1]
        if value > threshold * decreasing_factor:
            threshold = value
    return threshold
