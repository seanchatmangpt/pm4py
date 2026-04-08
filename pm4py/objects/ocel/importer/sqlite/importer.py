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



from pm4py.objects.ocel.obj import OCEL
from typing import Dict, Any
from enum import Enum
from typing import Optional
from pm4py.objects.ocel.importer.sqlite.variants import pandas_importer, ocel20
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS_IMPORTER = pandas_importer
    OCEL20 = ocel20


def apply(
    file_path: str,
    variant=Variants.PANDAS_IMPORTER,
    parameters: Optional[Dict[Any, Any]] = None,
) -> OCEL:
    """
    Imports an OCEL from a SQLite database

    Parameters
    --------------
    file_path
        Path to the SQLite database
    variant
        Variant of the importer to use:
        - Variants.PANDAS_IMPORTER => Pandas
    parameters
        Variant-specific parameters

    Returns
    --------------
    ocel
        Object-centric event log
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(
        file_path, parameters=parameters
    )
