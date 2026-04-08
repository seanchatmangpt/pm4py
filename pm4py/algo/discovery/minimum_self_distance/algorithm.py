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
from typing import Union, Optional, Dict, Any

import pandas as pd

from pm4py.algo.discovery.minimum_self_distance.variants import log, pandas
from pm4py.objects.log.obj import EventLog, EventStream
from pm4py.util import exec_utils, pandas_utils
from pm4py.utils import is_polars_lazyframe
import importlib.util

POLARS_AVAILABLE = importlib.util.find_spec("polars") is not None
if POLARS_AVAILABLE:
    from pm4py.algo.discovery.minimum_self_distance.variants import polars


class Variants(Enum):
    LOG = log
    PANDAS = pandas
    POLARS = polars if POLARS_AVAILABLE else log


def apply(
    log_obj: Union[EventLog, pd.DataFrame, EventStream],
    variant: Union[str, None] = None,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Dict[str, int]:
    if parameters is None:
        parameters = {}

    if variant is None:
        if is_polars_lazyframe(log_obj):
            if not POLARS_AVAILABLE:
                raise RuntimeError(
                    "Polars LazyFrame provided but 'polars' package is not installed."
                )
            variant = Variants.POLARS
        elif pandas_utils.check_is_pandas_dataframe(log_obj):
            variant = Variants.PANDAS
        else:
            variant = Variants.LOG

    return exec_utils.get_variant(variant).apply(
        log_obj, parameters=parameters
    )
