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


from pm4py.util.constants import STOCHASTIC_DISTRIBUTION


def apply(smap, parameters=None):
    """
    Embed the stochastic map into the Petri net

    Parameters
    ---------------
    smap
        Stochastic map
    parameters
        Possible parameters of the algorithm

    Returns
    ---------------
    void
    """
    if parameters is None:
        parameters = {}

    for t in smap:
        t.properties[STOCHASTIC_DISTRIBUTION] = smap[t]


def extract(net, parameters=None):
    """
    Extract the stochastic map from the Petri net

    Parameters
    --------------
    net
        Petri net
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    void
    """
    if parameters is None:
        parameters = {}

    smap = {}

    for t in net.transitions:
        smap[t] = t.properties[STOCHASTIC_DISTRIBUTION]

    return smap
