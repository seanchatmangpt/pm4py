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

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
from examples import examples_conf
import importlib.util


def execute_script():
    # import the log
    log_path = os.path.join("..", "tests", "input_data", "receipt.xes")
    log = xes_importer.apply(log_path)
    # apply Inductive Miner
    process_tree = inductive_miner.apply(log)
    net, initial_marking, final_marking = process_tree_converter.apply(process_tree)

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.petri_net import visualizer as pn_vis
        # get visualization
        variant = pn_vis.Variants.PERFORMANCE
        parameters_viz = {pn_vis.Variants.PERFORMANCE.value.Parameters.AGGREGATION_MEASURE: "mean", pn_vis.Variants.PERFORMANCE.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT}
        gviz = pn_vis.apply(net, initial_marking, final_marking, log=log, variant=variant,
                            parameters=parameters_viz)
        pn_vis.view(gviz)
        # do another visualization with frequency
        variant = pn_vis.Variants.FREQUENCY
        parameters_viz = {pn_vis.Variants.FREQUENCY.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT}
        gviz = pn_vis.apply(net, initial_marking, final_marking, log=log, variant=variant,
                            parameters=parameters_viz)
        pn_vis.view(gviz)


if __name__ == "__main__":
    execute_script()
