from enum import Enum
from typing import Optional, Dict, Any, Union
import polars as pl
from pm4py.util import exec_utils, constants, xes_constants


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY


def apply(
    lf: pl.LazyFrame,
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> Dict[str, Dict[str, int]]:
    """
    Computes for each trace of the event log how much rework occurs.
    The rework is computed as the difference between the total number of activities of a trace and the
    number of unique activities.

    Parameters
    ----------------
    lf
        Polars LazyFrame
    parameters
        Parameters of the algorithm, including:
        - Parameters.ACTIVITY_KEY => the activity key
        - Parameters.CASE_ID_KEY => the case identifier attribute

    Returns
    -----------------
    dict
        Dictionary associating to each case ID:
        - The number of total activities of the case (number of events)
        - The rework (difference between the total number of activities of a trace and the number of unique activities)
    """
    if parameters is None:
        parameters = {}

    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    case_id_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_CONCEPT_NAME
    )

    # Group by case and compute count and nunique for activities
    grouped_df = (
        lf.group_by(case_id_key)
        .agg([
            pl.col(activity_key).count().alias("count"),
            pl.col(activity_key).n_unique().alias("nunique")
        ])
        .collect()
    )

    rework_cases = {}
    for row in grouped_df.iter_rows():
        case_id = row[0]
        count = row[1]
        nunique = row[2]
        rework_cases[case_id] = {
            "number_activities": count,
            "rework": count - nunique,
        }

    return rework_cases