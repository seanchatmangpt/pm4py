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


import time
from enum import Enum
from typing import Optional, Dict, Any

import polars as pl

from pm4py.objects.dfg.obj import DFG
from pm4py.util import constants, exec_utils
from pm4py.util import xes_constants as xes_util


class Parameters(Enum):
    ACTIVITY_KEY = constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    CASE_ID_KEY = constants.PARAMETER_CONSTANT_CASEID_KEY
    TIMESTAMP_KEY = constants.PARAMETER_CONSTANT_TIMESTAMP_KEY


CONST_AUX_ACT = "aux_act_"
CONST_AUX_CASE = "aux_case_"
CONST_COUNT = "count_"


def apply(
    log: pl.DataFrame, parameters: Optional[Dict[str, Any]] = None
) -> DFG:
    parameters = {} if parameters is None else parameters
    act_key = exec_utils.get_param_value(
        Parameters.ACTIVITY_KEY, parameters, xes_util.DEFAULT_NAME_KEY
    )
    cid_key = exec_utils.get_param_value(
        Parameters.CASE_ID_KEY, parameters, constants.CASE_ATTRIBUTE_GLUE
    )
    time_key = exec_utils.get_param_value(
        Parameters.TIMESTAMP_KEY, parameters, xes_util.DEFAULT_TIMESTAMP_KEY
    )
    aux_act = CONST_AUX_ACT + str(time.time())
    aux_case = CONST_AUX_CASE + str(time.time())
    df = log[[cid_key, act_key, time_key]].clone()
    df = df.sort([cid_key, time_key])
    df = df[[cid_key, act_key]]
    df = df.with_column(df[act_key].shift(-1).alias(aux_act))
    df = df.with_column(df[cid_key].shift(-1).alias(aux_case))
    dfg = DFG()

    excl_starter = df[0, act_key]
    borders = df.filter(df[cid_key] != df[aux_case])

    for d in filter(
        lambda d: d[aux_act] is not None,
        borders.groupby([aux_act]).count().to_dicts(),
    ):
        v = d["count"] + 1 if d[aux_act] == excl_starter else d["count"]
        dfg.start_activities[d[aux_act]] = v

    for d in filter(
        lambda d: d[act_key] is not None,
        borders.groupby([act_key]).count().to_dicts(),
    ):
        dfg.end_activities[d[act_key]] = d["count"]

    for d in (
        df.filter((df[cid_key] == df[aux_case]))
        .groupby([act_key, aux_act])
        .count()
        .to_dicts()
    ):
        dfg.graph[(d[act_key], d[aux_act])] = d["count"]

    return dfg
