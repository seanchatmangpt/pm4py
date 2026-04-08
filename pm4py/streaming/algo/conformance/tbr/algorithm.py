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
from pm4py.util import exec_utils
from pm4py.streaming.algo.conformance.tbr.variants import classic


class Variants(Enum):
    CLASSIC = classic


def apply(net, im, fm, variant=Variants.CLASSIC, parameters=None):
    """
    Method that creates the TbrStreamingConformance object

    Parameters
    ----------------
    net
        Petri net
    im
        Initial marking
    fm
        Final marking
    variant
        Variant of the algorithm to use, possible:
            - Variants.CLASSIC
    parameters
        Parameters of the algorithm

    Returns
    ----------------
    conf_stream_obj
        Conformance streaming object
    """
    return exec_utils.get_variant(variant).apply(
        net, im, fm, parameters=parameters
    )
