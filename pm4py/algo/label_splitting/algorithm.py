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


from typing import Optional, Dict, Any, Union
from pm4py.objects.log.obj import EventLog, EventStream
import pandas as pd
from enum import Enum
from pm4py.util import exec_utils
from pm4py.algo.label_splitting.variants import contextual


class Variants(Enum):
    CONTEXTUAL = contextual


def apply(
    log: Union[EventLog, EventStream, pd.DataFrame],
    variant=Variants.CONTEXTUAL,
    parameters: Optional[Dict[Any, Any]] = None,
) -> pd.DataFrame:
    """
    Applies a technique of label-splitting, to distinguish between different meanings of the same
    activity. The result is a Pandas dataframe where the label-splitting has been applied.

    Minimum Viable Example:

        import pm4py
        from pm4py.algo.label_splitting import algorithm as label_splitter

        log = pm4py.read_xes("tests/input_data/receipt.xes")
        log2 = label_splitter.apply(log)


    Parameters
    ---------------
    log
        Event log
    parameters
        Variant-specific parameters

    Returns
    ---------------
    dataframe
        Pandas dataframe with the re-labeling
    """
    return exec_utils.get_variant(variant).apply(log, parameters)
