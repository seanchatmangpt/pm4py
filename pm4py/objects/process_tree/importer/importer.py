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

from pm4py.objects.process_tree.importer.variants import ptml
from pm4py.util import exec_utils


class Variants(Enum):
    PTML = ptml


DEFAULT_VARIANT = Variants.PTML


def apply(file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a process tree from the specified path

    Parameters
    ---------------
    path
        Path
    variant
        Variant of the algorithm, possible values:
            - Variants.PTML
    parameters
        Possible parameters (version specific)

    Returns
    ---------------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).apply(
        file_path, parameters=parameters
    )


def deserialize(tree_string, variant=DEFAULT_VARIANT, parameters=None):
    """
    Deserialize a text/binary string representing a process tree in the PTML format

    Parameters
    ----------
    tree_string
        Process tree expressed as PTML string
    variant
        Variant of the algorithm, possible values:
            - Variants.PTML
    parameters
        Other parameters of the algorithm

    Returns
    ----------
    tree
        Process tree
    """
    return exec_utils.get_variant(variant).import_tree_from_string(
        tree_string, parameters=parameters
    )
