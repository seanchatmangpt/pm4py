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


# Author: Maximilian Josef Frank (https://orcid.org/0000-0002-0714-7748)

from typing import Dict, FrozenSet, List

class GeneticMatrix:
    def __init__(
        self,
        input_map: Dict[str, List[FrozenSet[str]]],
        output_map: Dict[str, List[FrozenSet[str]]],
        transitions: List[str],
    ):
        """
        Initialize a Genetic matrix

        Reference paper:
        Maximilian Josef Frank. "Optimising and Implementing the Genetic Miner in PM4Py" (2026).

        Parameters
        -------------
        input_map
            Input map for each node
        output_map
            Output map for each node
        transitions
            List of transitions
        """
        self.input_map = input_map
        self.output_map = output_map
        self.transitions = transitions

    def __repr__(self):
        return str({
            "I": self.input_map,
            "O": self.output_map,
            "T": self.transitions
        })

    def __str__(self):
        return self.__repr__()
