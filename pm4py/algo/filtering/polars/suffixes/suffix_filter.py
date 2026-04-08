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


from pm4py.util.constants import CASE_CONCEPT_NAME, PARAMETER_CONSTANT_CASEID_KEY, PARAMETER_CONSTANT_ACTIVITY_KEY
from enum import Enum
from pm4py.util import exec_utils, constants, xes_constants
from typing import Optional, Dict, Any, Union, List
import polars as pl


class Parameters(Enum):
    CASE_ID_KEY = PARAMETER_CONSTANT_CASEID_KEY
    ACTIVITY_KEY = PARAMETER_CONSTANT_ACTIVITY_KEY
    POSITIVE = "positive"


def apply(
    df: pl.LazyFrame,
    suffixes: List[List[str]],
    parameters: Optional[Dict[Union[str, Parameters], Any]] = None,
) -> pl.LazyFrame:
    """
    Apply a filter on suffixes of the event log

    Parameters
    -----------
    df
        LazyFrame
    suffixes
        List of suffixes to filter on
    parameters
        Parameters of the algorithm

    Returns
    -----------
    df
        Filtered LazyFrame
    """
    if parameters is None:
        parameters = {}

    case_id_glue = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, CASE_CONCEPT_NAME
    )
    activity_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_constants.DEFAULT_NAME_KEY
    )
    positive = exec_utils.get_param_value(Parameters.POSITIVE, parameters, True)

    # Create case variants
    variants_df = (
        df.sort([case_id_glue, "time:timestamp"])
        .group_by(case_id_glue, maintain_order=True)
        .agg(pl.col(activity_key).alias("activities"))
    )

    # Check if any suffix matches
    suffix_conditions = []
    for suffix in suffixes:
        suffix_list = list(suffix)
        suffix_len = len(suffix_list)
        if suffix_len == 0:
            condition = pl.lit(True)
        else:
            condition = (
                pl.col("activities").list.tail(suffix_len)
                == pl.lit(suffix_list)
            )
        suffix_conditions.append(condition)

    if suffix_conditions:
        combined_condition = suffix_conditions[0]
        for cond in suffix_conditions[1:]:
            combined_condition = combined_condition | cond

        matching_cases = variants_df.filter(combined_condition).select(case_id_glue)
    else:
        matching_cases = pl.DataFrame({case_id_glue: []}).lazy()

    if positive:
        ret = df.join(matching_cases, on=case_id_glue, how="inner")
    else:
        ret = df.join(matching_cases, on=case_id_glue, how="anti")

    return ret
