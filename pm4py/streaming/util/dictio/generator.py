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

from pm4py.streaming.util.dictio.versions import classic, thread_safe, redis
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    THREAD_SAFE = thread_safe
    REDIS = redis


DEFAULT_VARIANT = Variants.THREAD_SAFE


def apply(variant=DEFAULT_VARIANT, parameters=None):
    """
    Generates a Python dictionary object
    (different implementations are possible)

    Parameters
    ----------------
    variant
        Variant to use
    parameters
        Parameters to use in the generation

    Returns
    -----------------
    dictio
        Dictionary
    """
    return exec_utils.get_variant(variant).apply(parameters=parameters)
