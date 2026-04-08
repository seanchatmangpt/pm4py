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
from pm4py.algo.discovery.dfg.adapters.pandas import df_statistics
from examples import examples_conf
import importlib.util


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes"), return_legacy_log_object=False)
    cost_based_dfg = df_statistics.get_dfg_graph(log, measure="cost", cost_attribute="amount")

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.dfg import visualizer as dfg_visualizer
        gviz = dfg_visualizer.apply(cost_based_dfg, variant=dfg_visualizer.Variants.COST, parameters={"format": examples_conf.TARGET_IMG_FORMAT})
        dfg_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
