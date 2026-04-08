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



from typing import Any, Collection, Dict

from pm4py.objects.petri_net.obj import PetriNet


class StochasticPetriNet(PetriNet):

    class Transition(PetriNet.Transition):
        def __init__(
            self,
            name: str,
            label: str = None,
            in_arcs: Collection[PetriNet.Arc] = None,
            out_arcs: Collection[PetriNet.Arc] = None,
            weight: float = 1.0,
            properties: Dict[str, Any] = None,
        ):
            super().__init__(name, label, in_arcs, out_arcs, properties)
            self.__weight = weight

        def __set_weight(self, weight: float):
            self.__weight = weight

        def __get_weight(self) -> float:
            return self.__weight

        weight = property(__get_weight, __set_weight)
