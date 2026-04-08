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
import pm4py
from examples import examples_conf
import importlib.util



def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))

    # frequency view of the network analysis

    # OUT column: case identifier
    # IN column: case identifier (the next event having the same case identifier is matched)
    # NODE column: the attribute to use to classify the node. In this case, we use the org:group (organizational group)
    # EDGE column: the attribute (of the source event) to use to classify the edge. In this case, we use the
    # concept:name (activity)

    frequency_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:group", node_column_target="org:group", edge_column="concept:name", performance=False)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_network_analysis(frequency_edges, variant="frequency", format=examples_conf.TARGET_IMG_FORMAT, edge_threshold=10)

    # performance view of the network analysis

    # OUT column: case identifier
    # IN column: case identifier (the next event having the same case identifier is matched)
    # NODE column: the attribute to use to classify the node. In this case, we use the org:group (organizational group)
    # EDGE column: the attribute (of the source event) to use to classify the edge. In this case, we use the
    # concept:name (activity)

    performance_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:group", node_column_target="org:group", edge_column="concept:name", performance=True)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_network_analysis(performance_edges, variant="performance", format=examples_conf.TARGET_IMG_FORMAT, edge_threshold=10)

    resource_group_edges = pm4py.discover_network_analysis(log, out_column="case:concept:name", in_column="case:concept:name", node_column_source="org:resource", node_column_target="org:group", edge_column="org:resource", performance=False)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_network_analysis(resource_group_edges, variant="frequency", format=examples_conf.TARGET_IMG_FORMAT, edge_threshold=10)


if __name__ == "__main__":
    execute_script()
