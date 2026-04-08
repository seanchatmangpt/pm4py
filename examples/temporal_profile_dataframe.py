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

from pm4py.algo.discovery.temporal_profile import algorithm as temporal_profile_discovery
from pm4py.algo.conformance.temporal_profile import algorithm as temporal_profile_conformance
from pm4py.util import constants, pandas_utils
from pm4py.objects.log.util import dataframe_utils


def execute_script():
    dataframe = pandas_utils.read_csv("../tests/input_data/receipt.csv")
    dataframe = dataframe_utils.convert_timestamp_columns_in_df(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)
    tf = temporal_profile_discovery.apply(dataframe)
    conformance = temporal_profile_conformance.apply(dataframe, tf, parameters={"zeta": 6.0})
    for index, dev in enumerate(conformance):
        if len(dev) > 0:
            print(index, dev)


if __name__ == "__main__":
    execute_script()
