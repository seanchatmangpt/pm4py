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


def derive_end_activities_from_log(log, activity_key):
    """
    Derive end activities from log

    Parameters
    -----------
    log
        Log object
    activity_key
        Activity key

    Returns
    -----------
    e
        End activities
    """
    e = set()
    for t in log:
        if len(t) > 0:
            if activity_key in t[len(t) - 1]:
                e.add(t[len(t) - 1][activity_key])
    return e


def derive_start_activities_from_log(log, activity_key):
    """
    Derive start activities from log

    Parameters
    -----------
    log
        Log object
    activity_key
        Activity key

    Returns
    -----------
    s
        Start activities
    """
    s = set()
    for t in log:
        if len(t) > 0:
            if activity_key in t[0]:
                s.add(t[0][activity_key])
    return s
