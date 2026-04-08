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


from typing import List, Dict


class Role(object):
    activities: List[str]
    originator_importance = Dict[str, float]

    def __init__(
        self, activities: List[str], originator_importance: Dict[str, float]
    ):
        self.activities = activities
        self.originator_importance = originator_importance

    def __repr__(self):
        return (
            "Activities: "
            + str(self.activities)
            + " Originators importance "
            + str(self.originator_importance)
        )

    def __str__(self):
        return (
            "Activities: "
            + str(self.activities)
            + " Originators importance "
            + str(self.originator_importance)
        )
