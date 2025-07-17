import pandas as pd
import numpy as np
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Parameters(Enum):
    MAX_DIVISIONS_X = "max_divisions_x"
    MAX_DIVISIONS_Y = "max_divisions_y"
    AGGREGATION_FUNCTION = "aggregation_function"
    X_BINS = "x_bins"           # Optional list of numeric bin edges for x_col
    Y_BINS = "y_bins"           # Optional list of numeric bin edges for y_col


def apply(
        feature_table: pd.DataFrame,
        x_col: str,
        y_col: str,
        agg_col: str,
        parameters: Optional[Dict[Any, Any]] = None
):
    """
    Constructs a process cube by slicing data along two dimensions
    (x_col, y_col) and aggregating a third (agg_col). Additionally:

    1) If x_col (or y_col) is an actual column in df, we do numeric binning.
       You can manually specify bin edges via parameters[Parameters.X_BINS]
       (a list of numeric edges) or parameters[Parameters.Y_BINS].
       Otherwise, we automatically divide into equal-width bins using
       parameters[Parameters.MAX_DIVISIONS_X] or MAX_DIVISIONS_Y.
    2) If x_col (or y_col) is not present, we do prefix-based binning.

    Parameters
    ----------
    feature_table : pd.DataFrame
        A feature table that must contain 'case:concept:name' and agg_col, plus
        the columns for x_col, y_col (if numeric) or the columns that start
        with x_col, y_col (if prefix-based).
    x_col : str
        The X dimension. If x_col in df.columns, numeric binning; else prefix-based.
    y_col : str
        The Y dimension. If y_col in df.columns, numeric binning; else prefix-based.
    agg_col : str
        The column to aggregate (mean, sum, etc.).
    parameters: Dict[Any, Any]
        Optional parameters of the method, including:
        * Parameters.X_BINS: List of numeric bin edges for x_col.
        * Parameters.Y_BINS: List of numeric bin edges for y_col.
        * Parameters.MAX_DIVISIONS_X: If x_col is numeric and X_BINS not provided,
          how many bins to divide it into.
        * Parameters.MAX_DIVISIONS_Y: If y_col is numeric and Y_BINS not provided,
          how many bins to divide it into.
        * Parameters.AGGREGATION_FUNCTION: The aggregation function,
          e.g., 'mean', 'sum', 'min', 'max'.

    Returns
    -------
    pivot_df : pd.DataFrame
        A pivoted DataFrame representing the process cube, with x bins as rows
        and y bins as columns, containing aggregated values of agg_col.
    cell_case_dict : dict
        A dictionary mapping (x_bin, y_bin) -> set of case IDs that fall in that cell.
    """
    if parameters is None:
        parameters = {}

    # Retrieve parameters, with None defaults for manual bins
    max_divisions_x = exec_utils.get_param_value(Parameters.MAX_DIVISIONS_X, parameters, 4)
    max_divisions_y = exec_utils.get_param_value(Parameters.MAX_DIVISIONS_Y, parameters, 4)
    agg_fn = exec_utils.get_param_value(Parameters.AGGREGATION_FUNCTION, parameters, "mean")
    x_bins_param = exec_utils.get_param_value(Parameters.X_BINS, parameters, None)
    y_bins_param = exec_utils.get_param_value(Parameters.Y_BINS, parameters, None)

    df = feature_table.copy()
    # ------------------------------------------------------
    # 1) Determine if X is numeric-based or prefix-based
    # ------------------------------------------------------
    if x_col in df.columns:
        numeric_x = True
        # Use manual bins if provided, else auto-generate equal-width bins
        if x_bins_param is not None:
            x_bins = sorted(x_bins_param)
        else:
            x_min, x_max = df[x_col].min(), df[x_col].max()
            x_bins = np.linspace(x_min, x_max, max_divisions_x + 1)
            print(x_bins)
        df["__x_bin_tmp__"] = pd.cut(df[x_col], bins=x_bins, include_lowest=True)
    else:
        numeric_x = False
        x_prefix_cols = [c for c in df.columns if c.startswith(x_col)]

    # ------------------------------------------------------
    # 2) Determine if Y is numeric-based or prefix-based
    # ------------------------------------------------------
    if y_col in df.columns:
        numeric_y = True
        if y_bins_param is not None:
            y_bins = sorted(y_bins_param)
        else:
            y_min, y_max = df[y_col].min(), df[y_col].max()
            y_bins = np.linspace(y_min, y_max, max_divisions_y + 1)
        df["__y_bin_tmp__"] = pd.cut(df[y_col], bins=y_bins, include_lowest=True)
    else:
        numeric_y = False
        y_prefix_cols = [c for c in df.columns if c.startswith(y_col)]

    # Build intermediate records
    records = []
    for _, row in df.iterrows():
        case_id = row["case:concept:name"]
        agg_value = row[agg_col]

        # X bins assignment
        if numeric_x:
            xb = row["__x_bin_tmp__"]
            if pd.isna(xb):
                continue
            x_bin_list = [xb]
        else:
            x_bin_list = [col for col in x_prefix_cols if pd.notna(row[col]) and row[col] >= 1]
            if not x_bin_list:
                continue

        # Y bins assignment
        if numeric_y:
            yb = row["__y_bin_tmp__"]
            if pd.isna(yb):
                continue
            y_bin_list = [yb]
        else:
            y_bin_list = [col for col in y_prefix_cols if pd.notna(row[col]) and row[col] >= 1]
            if not y_bin_list:
                continue

        # Cross-product
        for xb in x_bin_list:
            for yb in y_bin_list:
                records.append((case_id, xb, yb, agg_value))

    temp_df = pd.DataFrame(records, columns=["case:concept:name", "x_bin", "y_bin", agg_col])
    if temp_df.empty:
        return pd.DataFrame(), {}

    # Aggregation
    agg_df = temp_df.groupby(["x_bin", "y_bin"])[agg_col].agg(agg_fn).reset_index()
    cases_df = temp_df.groupby(["x_bin", "y_bin"])['case:concept:name'] \
        .agg(lambda x: set(x)).reset_index().rename(columns={"case:concept:name": "case_set"})
    merged_df = pd.merge(agg_df, cases_df, on=["x_bin", "y_bin"], how="outer")

    # Pivot
    pivot_df = merged_df.pivot(index="x_bin", columns="y_bin", values=agg_col)
    pivot_df = pivot_df.dropna(how="all", axis=0).dropna(how="all", axis=1)

    # Build cell-case mapping
    valid_x = set(pivot_df.index)
    valid_y = set(pivot_df.columns)
    cell_case_dict = {
        (row.x_bin, row.y_bin): row.case_set
        for row in cases_df.itertuples()
        if row.x_bin in valid_x and row.y_bin in valid_y
    }

    # Cleanup
    if numeric_x:
        df.drop(columns=["__x_bin_tmp__"], inplace=True)
    if numeric_y:
        df.drop(columns=["__y_bin_tmp__"], inplace=True)

    return pivot_df, cell_case_dict
