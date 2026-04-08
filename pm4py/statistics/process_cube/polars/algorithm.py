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
from typing import Optional, Dict, Any, Tuple

import polars as pl

from pm4py.statistics.process_cube.polars.variants import classic
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(
    feature_table: pl.LazyFrame | pl.DataFrame,
    x_col: str | Tuple[str, ...],
    y_col: str | Tuple[str, ...],
    agg_col: str,
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[pl.DataFrame, Dict[Any, Any]]:
    """Applies the selected process cube variant using Polars data structures.

    The X/Y dimension definitions can be provided as a string (single attribute) or
    as a tuple of attribute names to build composite bins.
    """

    return exec_utils.get_variant(variant).apply(
        feature_table, x_col, y_col, agg_col, parameters=parameters
    )
