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


from pm4py.objects.process_tree.exporter.variants import ptml
from pm4py.util import exec_utils
from enum import Enum


class Variants(Enum):
    PTML = ptml


DEFAULT_VARIANT = Variants.PTML


def apply(tree, output_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Exports the process tree to a file

    Parameters
    ----------------
    tree
        Process tree
    output_path
        Output path
    variant
        Variant of the algorithm:
            - Variants.PTML
    parameters
        Parameters
    """
    return exec_utils.get_variant(variant).apply(
        tree, output_path, parameters=parameters
    )


def serialize(tree, variant=DEFAULT_VARIANT, parameters=None):
    """
    Serializes the process tree into a binary string

    Parameters
    ----------------
    tree
        Process tree
    variant
        Variant of the algorithm:
            - Variants.PTML
    parameters
        Parameters

    Returns
    ---------------
    serialization
        Serialized string
    """
    return exec_utils.get_variant(variant).export_tree_as_string(
        tree, parameters=parameters
    )
