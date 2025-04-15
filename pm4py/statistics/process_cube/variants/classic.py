import pandas as pd
import numpy as np
from enum import Enum
from typing import Optional, Dict, Any
from pm4py.util import exec_utils


class Parameters(Enum):
    MAX_DIVISIONS_X = "max_divisions_x"
    MAX_DIVISIONS_Y = "max_divisions_y"
    AGGREGATION_FUNCTION = "aggregation_function"


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
       Otherwise, we do 'prefix-based' binning (include any column starting with x_col,
       and assign a row to that bin if >= 1).
    2) We return both the pivoted DataFrame and a dict associating each cell
       (x_bin, y_bin) -> set of case IDs.

    Parameters
    ----------
    feature_table : pd.DataFrame
        A feature table that must contain 'case:concept:name' and agg_col, plus
        the columns for x_col, y_col (if in numeric mode) or the columns that start
        with x_col, y_col (if in prefix mode).
    x_col : str
        The X dimension. If x_col in df.columns, use numeric binning. Otherwise, treat
        it as a prefix for 'prefix-based' binning.
    y_col : str
        The Y dimension. If y_col in df.columns, use numeric binning. Otherwise, treat
        it as a prefix for 'prefix-based' binning.
    agg_col : str
        The column to aggregate (mean, sum, etc.).
    parameters: Dict[Any, Any]
        Optional parameters of the method, including:
        * Parameters.MAX_DIVISIONS_X: If x_col is numeric, how many bins to divide it into.
        * Parameters.MAX_DIVISIONS_Y: If y_col is numeric, how many bins to divide it into.
        * Parameters.AGGREGATION_FUNCTION: The aggregation function, e.g., 'mean', 'sum', 'min', 'max'.

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

    max_divisions_x = exec_utils.get_param_value(Parameters.MAX_DIVISIONS_X, parameters, 4)
    max_divisions_y = exec_utils.get_param_value(Parameters.MAX_DIVISIONS_Y, parameters, 4)
    agg_fn = exec_utils.get_param_value(Parameters.AGGREGATION_FUNCTION, parameters, "mean")

    df = feature_table
    # ------------------------------------------------------
    # 1) Determine if X is numeric-based or prefix-based
    # ------------------------------------------------------
    if x_col in df.columns:
        numeric_x = True
        # Create numeric bins for x_col
        x_min, x_max = df[x_col].min(), df[x_col].max()
        x_bins = np.linspace(x_min, x_max, max_divisions_x + 1)
        # Use pd.cut to assign each row exactly one x_bin
        df["__x_bin_tmp__"] = pd.cut(df[x_col], bins=x_bins, include_lowest=True)
    else:
        numeric_x = False
        # Gather all columns that start with x_col
        x_prefix_cols = [c for c in df.columns if c.startswith(x_col)]

    # ------------------------------------------------------
    # 2) Determine if Y is numeric-based or prefix-based
    # ------------------------------------------------------
    if y_col in df.columns:
        numeric_y = True
        # Create numeric bins for y_col
        y_min, y_max = df[y_col].min(), df[y_col].max()
        y_bins = np.linspace(y_min, y_max, max_divisions_y + 1)
        # Use pd.cut to assign each row exactly one y_bin
        df["__y_bin_tmp__"] = pd.cut(df[y_col], bins=y_bins, include_lowest=True)
    else:
        numeric_y = False
        y_prefix_cols = [c for c in df.columns if c.startswith(y_col)]

    # We will build an intermediate "long" table with columns:
    # [case:concept:name, x_bin, y_bin, agg_col]
    records = []

    # ------------------------------------------------------
    # 3) Iterate over rows to assign them to bin(s)
    #    - For numeric bin: exactly 1 bin
    #    - For prefix-based bin: possibly multiple if >= 1
    # ------------------------------------------------------
    for idx, row in df.iterrows():
        case_id = row["case:concept:name"]
        agg_value = row[agg_col]

        # A) Determine x_bins for this row
        if numeric_x:
            # Exactly one bin from the tmp column
            x_bin_value = row["__x_bin_tmp__"]  # Interval, or NaN if out of range
            if pd.isna(x_bin_value):
                # If for some reason it's NaN, skip
                continue
            x_bin_list = [x_bin_value]
        else:
            # prefix-based
            # collect all columns that start with x_col where row[column] >= 1
            x_bin_list = []
            for colname in x_prefix_cols:
                val = row[colname]
                if pd.notna(val) and val >= 1:
                    # we treat the 'bin' as the column name itself
                    x_bin_list.append(colname)

            # If none apply, skip this row entirely (no X membership)
            if len(x_bin_list) == 0:
                continue

        # B) Determine y_bins for this row
        if numeric_y:
            y_bin_value = row["__y_bin_tmp__"]
            if pd.isna(y_bin_value):
                continue
            y_bin_list = [y_bin_value]
        else:
            # prefix-based
            y_bin_list = []
            for colname in y_prefix_cols:
                val = row[colname]
                if pd.notna(val) and val >= 1:
                    y_bin_list.append(colname)

            if len(y_bin_list) == 0:
                continue

        # C) Add cross-product of x_bin_list and y_bin_list to 'records'
        for xb in x_bin_list:
            for yb in y_bin_list:
                records.append((case_id, xb, yb, agg_value))

    # ------------------------------------------------------
    # 4) Create a temp DataFrame from these records
    # ------------------------------------------------------
    temp_df = pd.DataFrame(records, columns=["case:concept:name", "x_bin", "y_bin", agg_col])

    # If nothing ended up in records (e.g., no membership), we can return empty quickly
    if len(temp_df) == 0:
        empty_pivot = pd.DataFrame()
        return empty_pivot, {}

    # ------------------------------------------------------
    # 5) Perform the group-by aggregator
    # ------------------------------------------------------
    agg_df = temp_df.groupby(["x_bin", "y_bin"])[agg_col].agg(agg_fn).reset_index()

    # Create also a group-by for case IDs
    cases_df = temp_df.groupby(["x_bin", "y_bin"])["case:concept:name"] \
        .agg(lambda x: set(x)).reset_index()
    cases_df.rename(columns={"case:concept:name": "case_set"}, inplace=True)

    # Merge aggregator results and case sets
    merged_df = pd.merge(agg_df, cases_df, on=["x_bin", "y_bin"], how="outer")

    # ------------------------------------------------------
    # 6) Pivot to get a matrix with:
    #    - Rows = x_bin
    #    - Columns = y_bin
    #    - Values = aggregator of agg_col
    # ------------------------------------------------------
    pivot_df = merged_df.pivot(index="x_bin", columns="y_bin", values=agg_col)

    # ------------------------------------------------------
    # 7) Remove rows and columns that are completely empty (all NaN)
    # ------------------------------------------------------
    pivot_df = pivot_df.dropna(how="all", axis=0)  # drop any row that's all NaN
    pivot_df = pivot_df.dropna(how="all", axis=1)  # drop any column that's all NaN

    # ------------------------------------------------------
    # 8) Build a dictionary (x_bin, y_bin) -> set of case IDs
    # ------------------------------------------------------
    cell_case_dict = {}
    for _, row_ in merged_df.iterrows():
        xb = row_["x_bin"]
        yb = row_["y_bin"]
        # The aggregator row might or might not be in the final pivot if it's all-NaN,
        # but we still create the dictionary entry. We'll filter out if needed.
        case_set = row_["case_set"]
        cell_case_dict[(xb, yb)] = case_set

    # Optionally remove keys from cell_case_dict that did not appear in the final pivot
    # (i.e., rows/cols dropped as all-NaN). One approach:
    valid_x_bins = set(pivot_df.index)
    valid_y_bins = set(pivot_df.columns)
    # keep only cells that remain in pivot
    cell_case_dict = {
        (xb, yb): s
        for (xb, yb), s in cell_case_dict.items()
        if (xb in valid_x_bins) and (yb in valid_y_bins)
    }

    # ------------------------------------------------------
    # 9) (Optional) Clean up temporary columns if numeric approach used
    # ------------------------------------------------------
    if numeric_x:
        df.drop(columns=["__x_bin_tmp__"], inplace=True)
    if numeric_y:
        df.drop(columns=["__y_bin_tmp__"], inplace=True)

    return pivot_df, cell_case_dict
