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
from pm4py.util import constants, pandas_utils
import time


def execute_script():
    dataframe = pandas_utils.read_csv("../tests/input_data/receipt.csv")
    dataframe = pm4py.format_dataframe(dataframe, timest_format=constants.DEFAULT_TIMESTAMP_PARSE_FORMAT)

    # prints the original timestamp column of the dataframe
    print(dataframe["time:timestamp"])

    # Here are some common options that you can use as a granularity:
    #
    # 'h': Hour
    # 'min': Minute
    # 's': Second
    # 'ms': Millisecond
    # 'ns': Nanosecond

    st = time.time_ns()
    # cast on the minute
    dataframe["time:timestamp"] = dataframe["time:timestamp"].dt.floor(freq='min')
    ct = time.time_ns()

    print("required time for the timestamp casting: %.2f seconds" % ((ct-st)/10**9))

    # prints the new timestamp column of the dataframe
    print(dataframe["time:timestamp"])

    # for completeness, we report some alternatives methods in Pandas to do the same (casting on the minute):
    #
    # dataframe["time:timestamp"] = dataframe["time:timestamp"].apply(lambda x: x.replace(second=0, microsecond=0))
    #
    # dataframe["time:timestamp"] = dataframe["time:timestamp"].dt.round('min')


if __name__ == "__main__":
    execute_script()
