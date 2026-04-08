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


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")

    # gets the frequent trace segments
    traces = pm4py.get_frequent_trace_segments(log, min_occ=100)

    for t in traces:
        # filter on the given trace segment, to obtain an event log where all the cases contain the trace segment
        print(t)
        filtered_log = pm4py.filter_trace_segments(log, [t])
        print(filtered_log)

        break


if __name__ == "__main__":
    execute_script()
