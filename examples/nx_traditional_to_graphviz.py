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
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    # gets an 'event graph' where events, cases and their relationships
    # are represented in a graph (NetworkX DiGraph)
    event_graph = pm4py.convert_log_to_networkx(log)

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.networkx import visualizer as nx_to_gv_vis

        # visualize the NX DiGraph using Graphviz
        gviz = nx_to_gv_vis.apply(event_graph, parameters={"format": examples_conf.TARGET_IMG_FORMAT})
        nx_to_gv_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
