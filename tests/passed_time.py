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

import os
import unittest

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants, pandas_utils
from pm4py.statistics.passed_time.log import algorithm as log_passed_time
from pm4py.statistics.passed_time.pandas import algorithm as df_passed_time


class PassedTimeTest(unittest.TestCase):
    def test_passedtime_prepost_log(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        prepost = log_passed_time.apply(log, "decide", variant=log_passed_time.Variants.PREPOST)
        del prepost

    def test_passedtime_prepost_df(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        prepost = df_passed_time.apply(df, "decide", variant=df_passed_time.Variants.PREPOST)
        del prepost


if __name__ == "__main__":
    unittest.main()
