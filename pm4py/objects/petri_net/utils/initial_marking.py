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


from pm4py.objects.petri_net.obj import Marking


def discover_initial_marking(petri):
    """
    Discovers initial marking from a Petri net

    Parameters
    ------------
    petri
        Petri net

    Returns
    ------------
    initial_marking
        Initial marking of the Petri net
    """
    initial_marking = Marking()

    for place in petri.places:
        if len(place.in_arcs) == 0:
            initial_marking[place] = 1

    return initial_marking
