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


from pm4py.util.constants import CASE_CONCEPT_NAME
from pm4py.util import xes_constants as xes
from pm4py.util.xes_constants import DEFAULT_NAME_KEY
from pm4py.util.constants import PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    POSITIVE = "positive"


def apply(
    df: pl.LazyFrame,
    values: List[str],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Filter LazyFrame on start activities

    Parameters
    ----------
    df
        LazyFrame
    values
        Values to filter on
    parameters
        Parameters of the algorithm, including:
            Parameters.CASE_ID_KEY -> Case ID column
            Parameters.ACTIVITY_KEY -> Activity column
            Parameters.POSITIVE -> Include traces (True) or exclude traces (False)

    Returns
    ----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, DEFAULT_NAME_KEY
    )
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    # Get cases with matching start activities
    matching_cases = (
        df.group_by(case_id_glue)
        .agg(pl.col(activity_key).first().alias("start_activity"))
        .filter(pl.col("start_activity").is_in(values))
        .select(case_id_glue)
    )

    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti")

    return ret
