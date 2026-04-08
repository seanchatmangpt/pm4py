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

from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
from examples import examples_conf
import importlib.util


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_path)
    print("loaded log")
    process_tree = inductive_miner.apply(log)
    net, marking, final_marking = process_tree_converter.apply(process_tree)
    for place in marking:
        print("initial marking " + place.name)
    for place in final_marking:
        print("final marking " + place.name)

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.petri_net import visualizer as pn_vis
        gviz = pn_vis.apply(net, marking, final_marking,
                            parameters={pn_vis.Variants.WO_DECORATION.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        pn_vis.view(gviz)

    print("started token replay")
    aligned_traces = token_replay.apply(log, net, marking, final_marking)
    fit_traces = [x for x in aligned_traces if x['trace_is_fit']]
    perc_fitness = 0.00
    if len(aligned_traces) > 0:
        perc_fitness = len(fit_traces) / len(aligned_traces)
    print("perc_fitness=", perc_fitness)


if __name__ == "__main__":
    execute_script()
