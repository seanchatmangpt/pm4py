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
from pm4py.algo.filtering.pandas.timestamp_case_grouping import timestamp_case_grouping_filter


def execute_script():
    dataframe = pm4py.read_xes("../tests/input_data/roadtraffic100traces.xes")
    print(dataframe)
    filtered_dataframe = timestamp_case_grouping_filter.apply(dataframe, parameters={"filter_type": "concat"})
    print(filtered_dataframe)
    print(filtered_dataframe["concept:name"].value_counts())


if __name__ == "__main__":
    execute_script()
