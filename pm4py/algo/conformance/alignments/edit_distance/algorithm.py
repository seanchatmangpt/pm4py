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
from typing import Optional, Dict, Any, Union

from pm4py.algo.conformance.alignments.edit_distance.variants import (
    edit_distance,
)
from pm4py.objects.log.obj import EventLog
from pm4py.util import exec_utils
from pm4py.util import typing
import pandas as pd


class Variants(Enum):
    EDIT_DISTANCE = edit_distance


def apply(
    log1: Union[EventLog, pd.DataFrame],
    log2: Union[EventLog, pd.DataFrame],
    variant=Variants.EDIT_DISTANCE,
    parameters: Optional[Dict[Any, Any]] = None,
) -> typing.ListAlignments:
    """
    Aligns each trace of the first log against the second log

    Parameters
    --------------
    log1
        First log
    log2
        Second log
    variant
        Variant of the algorithm, possible values:
        - Variants.EDIT_DISTANCE: minimizes the edit distance
    parameters
        Parameters of the algorithm

    Returns
    ---------------
    aligned_traces
        List that contains, for each trace of the first log, the corresponding alignment
    """
    return exec_utils.get_variant(variant).apply(
        log1, log2, parameters=parameters
    )
