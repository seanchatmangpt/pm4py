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

from pm4py.objects.conversion.bpmn.variants import to_petri_net
from pm4py.util import exec_utils


class Variants(Enum):
    TO_PETRI_NET = to_petri_net


DEFAULT_VARIANT = Variants.TO_PETRI_NET


def apply(obj, variant=DEFAULT_VARIANT, parameters=None):
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(obj, parameters=parameters)
