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
from pm4py.algo.conformance.alignments.process_tree.util import search_graph_pt_frequency_annotation
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from examples import examples_conf
import importlib.util


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    tree = pm4py.discover_process_tree_inductive(log)
    aligned_traces = pm4py.conformance_diagnostics_alignments(log, tree, return_diagnostics_dataframe=False)
    tree = search_graph_pt_frequency_annotation.apply(tree, aligned_traces)

    if importlib.util.find_spec("graphviz"):
        gviz = pt_visualizer.apply(tree, parameters={"format": examples_conf.TARGET_IMG_FORMAT}, variant=pt_visualizer.Variants.FREQUENCY_ANNOTATION)
        pt_visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
