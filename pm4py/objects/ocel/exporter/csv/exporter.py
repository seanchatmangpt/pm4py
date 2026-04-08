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

from pm4py.objects.ocel.exporter.csv.variants import pandas
from pm4py.objects.ocel.obj import OCEL
from pm4py.util import exec_utils


class Variants(Enum):
    PANDAS = pandas


def apply(
    ocel: OCEL,
    output_path: str,
    variant=Variants.PANDAS,
    objects_path=None,
    parameters: Optional[Dict[Any, Any]] = None,
):
    """
    Exports an object-centric event log in a CSV file

    Parameters
    -----------------
    ocel
        Object-centric event log
    output_path
        Destination file
    variant
        Variant of the algorithm that should be used, possible values:
        - Variants.PANDAS
    objects_path
        Optional path, where the objects dataframe is stored
    parameters
        Parameters of the algorithm
    """
    return exec_utils.get_variant(variant).apply(
        ocel, output_path, objects_path=objects_path, parameters=parameters
    )
