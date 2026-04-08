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
from examples import examples_conf
import importlib.util


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")
    dfg, start_act, end_act = pm4py.discover_dfg(log)
    # keep the specified amount of activities
    dfg, start_act, end_act = pm4py.filter_dfg_activities_percentage(dfg, start_act, end_act, percentage=0.3)
    # keep the specified amount of paths
    dfg, start_act, end_act = pm4py.filter_dfg_paths_percentage(dfg, start_act, end_act, percentage=0.3)

    if importlib.util.find_spec("graphviz"):
        # view the DFG
        pm4py.view_dfg(dfg, start_act, end_act, format="svg")


if __name__ == "__main__":
    execute_script()
