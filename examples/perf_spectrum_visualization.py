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

import pm4py
import os
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils
from examples import examples_conf
import importlib.util


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))

    if importlib.util.find_spec("graphviz"):
        pm4py.view_performance_spectrum(log, ["Confirmation of receipt", "T04 Determine confirmation of receipt",
                                             "T10 Determine necessity to stop indication"], format=examples_conf.TARGET_IMG_FORMAT)

    df = pandas_utils.read_csv(os.path.join("..", "tests", "input_data", "receipt.csv"))
    df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT, timest_columns=["time:timestamp"])

    if importlib.util.find_spec("graphviz"):
        pm4py.view_performance_spectrum(df, ["Confirmation of receipt", "T04 Determine confirmation of receipt",
                                             "T10 Determine necessity to stop indication"], format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
