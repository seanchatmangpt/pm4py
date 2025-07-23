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

    # Work with a view instead of copy when possible
    df = feature_table
    
    # Pre-compute column lists and masks for better performance
    numeric_x = x_col in df.columns
    numeric_y = y_col in df.columns
    
    if not numeric_x:
        x_prefix_cols = [c for c in df.columns if c.startswith(x_col)]
    if not numeric_y:
        y_prefix_cols = [c for c in df.columns if c.startswith(y_col)]

    # ------------------------------------------------------
    # Handle X dimension binning
    # ------------------------------------------------------
    if numeric_x:
        # Use manual bins if provided, else auto-generate equal-width bins
        if x_bins_param is not None:
            x_bins = sorted(x_bins_param)
        else:
            x_min, x_max = df[x_col].min(), df[x_col].max()
            x_bins = np.linspace(x_min, x_max, max_divisions_x + 1)
        
        # Create binned column directly without temporary column
        x_binned = pd.cut(df[x_col], bins=x_bins, include_lowest=True)
        x_valid_mask = pd.notna(x_binned)
    else:
        # Pre-filter and vectorize prefix-based column selection
        x_prefix_data = df[x_prefix_cols].fillna(0)
        x_valid_cols_mask = x_prefix_data >= 1
        x_valid_mask = x_valid_cols_mask.any(axis=1)

    # ------------------------------------------------------
    # Handle Y dimension binning
    # ------------------------------------------------------
    if numeric_y:
        if y_bins_param is not None:
            y_bins = sorted(y_bins_param)
        else:
            y_min, y_max = df[y_col].min(), df[y_col].max()
            y_bins = np.linspace(y_min, y_max, max_divisions_y + 1)
        
        y_binned = pd.cut(df[y_col], bins=y_bins, include_lowest=True)
        y_valid_mask = pd.notna(y_binned)
    else:
        y_prefix_data = df[y_prefix_cols].fillna(0)
        y_valid_cols_mask = y_prefix_data >= 1
        y_valid_mask = y_valid_cols_mask.any(axis=1)

    # Combined validity mask
    valid_mask = x_valid_mask & y_valid_mask
    if not valid_mask.any():
        return pd.DataFrame(), {}

    # Filter data to valid rows only
    valid_df = df[valid_mask]
    case_ids = valid_df["case:concept:name"].values
    agg_values = valid_df[agg_col].values

    # Build records more efficiently using vectorized operations
    records = []
    
    if numeric_x and numeric_y:
        # Both numeric - simplest case
        x_bins_valid = x_binned[valid_mask]
        y_bins_valid = y_binned[valid_mask]
        
        for i, (case_id, agg_val, x_bin, y_bin) in enumerate(zip(case_ids, agg_values, x_bins_valid, y_bins_valid)):
            records.append((case_id, x_bin, y_bin, agg_val))
            
    elif numeric_x and not numeric_y:
        # X numeric, Y prefix-based
        x_bins_valid = x_binned[valid_mask]
        y_prefix_valid = y_prefix_data[valid_mask]
        y_valid_cols_valid = y_valid_cols_mask[valid_mask]
        
        for i, (case_id, agg_val, x_bin) in enumerate(zip(case_ids, agg_values, x_bins_valid)):
            y_cols = [col for j, col in enumerate(y_prefix_cols) if y_valid_cols_valid.iloc[i, j]]
            for y_col_name in y_cols:
                records.append((case_id, x_bin, y_col_name, agg_val))
                
    elif not numeric_x and numeric_y:
        # X prefix-based, Y numeric
        x_prefix_valid = x_prefix_data[valid_mask]
        x_valid_cols_valid = x_valid_cols_mask[valid_mask]
        y_bins_valid = y_binned[valid_mask]
        
        for i, (case_id, agg_val, y_bin) in enumerate(zip(case_ids, agg_values, y_bins_valid)):
            x_cols = [col for j, col in enumerate(x_prefix_cols) if x_valid_cols_valid.iloc[i, j]]
            for x_col_name in x_cols:
                records.append((case_id, x_col_name, y_bin, agg_val))
                
    else:
        # Both prefix-based
        x_prefix_valid = x_prefix_data[valid_mask]
        x_valid_cols_valid = x_valid_cols_mask[valid_mask]
        y_prefix_valid = y_prefix_data[valid_mask]
        y_valid_cols_valid = y_valid_cols_mask[valid_mask]
        
        for i, (case_id, agg_val) in enumerate(zip(case_ids, agg_values)):
            x_cols = [col for j, col in enumerate(x_prefix_cols) if x_valid_cols_valid.iloc[i, j]]
            y_cols = [col for j, col in enumerate(y_prefix_cols) if y_valid_cols_valid.iloc[i, j]]
            
            for x_col_name in x_cols:
                for y_col_name in y_cols:
                    records.append((case_id, x_col_name, y_col_name, agg_val))

    if not records:
        return pd.DataFrame(), {}

    # Create DataFrame more efficiently
    temp_df = pd.DataFrame(records, columns=["case:concept:name", "x_bin", "y_bin", agg_col])

    # Optimized aggregation using single groupby operation
    grouped = temp_df.groupby(["x_bin", "y_bin"])
    agg_result = grouped.agg({
        agg_col: agg_fn,
        "case:concept:name": lambda x: set(x)
    }).reset_index()
    agg_result.rename(columns={"case:concept:name": "case_set"}, inplace=True)

    # Pivot table creation
    pivot_df = agg_result.pivot(index="x_bin", columns="y_bin", values=agg_col)
    pivot_df = pivot_df.dropna(how="all", axis=0).dropna(how="all", axis=1)

    # Build cell-case mapping more efficiently
    valid_x = set(pivot_df.index)
    valid_y = set(pivot_df.columns)
    
    # Filter case data and create dictionary in one step
    cell_case_dict = {
        (row["x_bin"], row["y_bin"]): row["case_set"]
        for _, row in agg_result.iterrows()
        if row["x_bin"] in valid_x and row["y_bin"] in valid_y
    }

    return pivot_df, cell_case_dict
