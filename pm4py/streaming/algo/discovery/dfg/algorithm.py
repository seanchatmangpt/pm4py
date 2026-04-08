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


from pm4py.streaming.algo.discovery.dfg.variants import frequency
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    FREQUENCY = frequency


DEFAULT_VARIANT = Variants.FREQUENCY


def apply(variant=DEFAULT_VARIANT, parameters=None):
    """
    Discovers a DFG from an event stream

    Parameters
    --------------
    variant
        Variant of the algorithm (default: Variants.FREQUENCY)

    Returns
    --------------
    stream_dfg_obj
        Streaming DFG discovery object
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(parameters=parameters)
