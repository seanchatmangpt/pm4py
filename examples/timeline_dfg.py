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
from pm4py.algo.discovery.dfg.variants import clean_time
from pm4py.visualization.dfg.variants import timeline as timeline_gviz_generator
from pm4py.visualization.dfg import visualizer as dfg_visualizer


def execute_script():
    dataframe = pm4py.read_xes("../tests/input_data/running-example.xes")

    dfg, start_act, end_act = pm4py.discover_dfg_typed(dataframe)

    dfg_time = clean_time.apply(dataframe)

    gviz = timeline_gviz_generator.apply(dfg, dfg_time, parameters={"format": "svg", "start_activities": start_act,
                                                                    "end_activities": end_act})
    dfg_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
