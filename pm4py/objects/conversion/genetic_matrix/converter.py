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

from pm4py.objects.conversion.genetic_matrix.variants import to_petri_net
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    TO_PETRI_NET = to_petri_net


def apply(genetic_matrix, parameters=None, variant=Variants.TO_PETRI_NET):
    """
    Converts a GeneticMatrix to a different type of object

    Parameters
    --------------
    genetic_matrix
        Genetic matrix
    parameters
        Possible parameters of the algorithm
    variant
        Variant of the algorithm:
            - Variants.TO_PETRI_NET
    """
    return exec_utils.get_variant(variant).apply(
        genetic_matrix, parameters=parameters
    )
