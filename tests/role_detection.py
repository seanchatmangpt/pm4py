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

import unittest
import os

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.util import constants, pandas_utils
from pm4py.algo.organizational_mining.roles import algorithm as role_mining


class RoleDetectionTest(unittest.TestCase):
    def test_role_running_csv(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "running-example.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        roles = role_mining.apply(df)

    def test_role_running_xes(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
        roles = role_mining.apply(log)

    def test_role_receipt_csv(self):
        df = pandas_utils.read_csv(os.path.join("input_data", "receipt.csv"))
        df = dataframe_utils.convert_timestamp_columns_in_df(df, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
        roles = role_mining.apply(df)

    def test_role_receipt_xes(self):
        log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
        roles = role_mining.apply(log)


if __name__ == "__main__":
    unittest.main()
