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
from pm4py.objects.ocel.exporter.sqlite.variants import pandas_exporter, ocel20
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any


class Variants(Enum):
    PANDAS_EXPORTER = pandas_exporter
    OCEL20 = ocel20


def apply(
    ocel: OCEL,
    target_path: str,
    variant=Variants.PANDAS_EXPORTER,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Exports an OCEL to a SQLite database

    Parameters
    -------------
    ocel
        Object-centric event log
    target_path
        Path to the SQLite database
    variant
        Variant to use. Possible values:
        - Variants.PANDAS_EXPORTER => Pandas exporter
    parameters
        Variant-specific parameters
    """
    if parameters is None:
        parameters = {}

    return exec_utils.get_variant(variant).apply(
        ocel, target_path, parameters=parameters
    )
