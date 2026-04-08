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

from pm4py.objects.dfg.importer.variants import classic
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


DEFAULT_VARIANT = Variants.CLASSIC


def apply(file_path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Import a DFG (along with the start and end activities)

    Parameters
    --------------
    file_path
        Path of the DFG file
    variant
        Variant of the importer, possible values:
            - Variants.CLASSIC: importing from a .dfg file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    return exec_utils.get_variant(variant).apply(
        file_path, parameters=parameters
    )


def deserialize(dfg_string, variant=DEFAULT_VARIANT, parameters=None):
    """
    Import a DFG from a binary/textual string

    Parameters
    --------------
    dfg_string
        DFG represented as a string in the .dfg format
    variant
        Variant of the importer, possible values:
            - Variants.CLASSIC: importing from a .dfg file
    parameters
        Possible parameters of the algorithm

    Returns
    --------------
    dfg
        DFG
    start_activities
        Start activities
    end_activities
        End activities
    """
    return exec_utils.get_variant(variant).import_dfg_from_string(
        dfg_string, parameters=parameters
    )
