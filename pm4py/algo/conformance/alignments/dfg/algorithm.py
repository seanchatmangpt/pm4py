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


from pm4py.algo.conformance.alignments.dfg.variants import classic
from enum import Enum
from pm4py.util import exec_utils
from pm4py.objects.log.obj import EventLog, Trace
from typing import Optional, Dict, Any, Union, Tuple
from pm4py.util import typing
import pandas as pd


class Variants(Enum):
    CLASSIC = classic


def apply(
    obj: Union[EventLog, pd.DataFrame, Trace],
    dfg: Dict[Tuple[str, str], int],
    sa: Dict[str, int],
    ea: Dict[str, int],
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Union[typing.AlignmentResult, typing.ListAlignments]:
    """
    Applies the alignment algorithm provided a log/trace object, and a *connected* DFG

    Parameters
    --------------
    obj
        Event log / Trace
    dfg
        *Connected* directly-Follows Graph
    sa
        Start activities
    ea
        End activities
    variant
        Variant of the DFG alignments to be used. Possible values:
        - Variants.CLASSIC
    parameters
        Variant-specific parameters.

    Returns
    --------------
    ali
        Result of the alignment
    """
    return exec_utils.get_variant(variant).apply(
        obj, dfg, sa, ea, parameters=parameters
    )
