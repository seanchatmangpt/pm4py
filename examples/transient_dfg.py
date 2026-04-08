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

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.dfg import algorithm as dfg_miner
from pm4py.objects.stochastic_petri import ctmc
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    performance_dfg = dfg_miner.apply(log, variant=dfg_miner.Variants.PERFORMANCE)
    reach_graph, tang_reach_graph, stochastic_map, q_matrix = ctmc.get_tangible_reachability_and_q_matrix_from_dfg_performance(
        performance_dfg)
    # pick the source state
    state = [x for x in tang_reach_graph.states if x.name == "source1"][0]
    # analyse the distribution over the states of the system starting from the source after 86400.0 seconds (1 day)
    transient_result = ctmc.transient_analysis_from_tangible_q_matrix_and_single_state(tang_reach_graph, q_matrix, state, 86400.0)
    print(transient_result)


if __name__ == "__main__":
    execute_script()
