from enum import Enum
from typing import Optional, Dict, Any, Tuple

import polars as pl

from pm4py.statistics.process_cube.polars.variants import classic
from pm4py.util import exec_utils


class Variants(Enum):
    CLASSIC = classic


def apply(
    feature_table: pl.LazyFrame | pl.DataFrame,
    x_col: str,
    y_col: str,
    agg_col: str,
    variant=Variants.CLASSIC,
    parameters: Optional[Dict[Any, Any]] = None,
) -> Tuple[pl.DataFrame, Dict[Any, Any]]:
    """Applies the selected process cube variant using Polars data structures."""

    return exec_utils.get_variant(variant).apply(
        feature_table, x_col, y_col, agg_col, parameters=parameters
    )
