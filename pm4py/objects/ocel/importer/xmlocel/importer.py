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
from typing import Optional, Dict, Any

from pm4py.objects.ocel.importer.xmlocel.variants import (
    classic,
    ocel20,
    ocel20_rustxes,
)
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic
    OCEL20 = ocel20
    OCEL20_RUSTXES = ocel20_rustxes


def apply(
    file_path: str,
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Imports an object-centric event log from a XML-OCEL file

    Parameters
    -----------------
    file_path
        Path to the XML-OCEL file
    variant
        Variant of the algorithm to use, possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters

    Returns
    ------------------
    ocel
        Object-centric event log
    """
    return exec_utils.get_variant(variant).apply(file_path, parameters)
