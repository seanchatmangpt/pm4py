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
import importlib.util
from pm4py.algo.discovery.inductive import algorithm as inductive
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.conformance.alignments.process_tree import algorithm as align_approx
from pm4py.objects.petri_net.utils.align_utils import pretty_print_alignments
from examples import examples_conf


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")

    log = xes_importer.apply(log_path)
    tree = inductive.apply(log)

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.process_tree import visualizer as pt_vis
        gviz = pt_vis.apply(tree, parameters={pt_vis.Variants.WO_DECORATION.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        pt_vis.view(gviz)

    print("start calculate approximated alignments")
    approx_alignments = align_approx.apply(log, tree)
    pretty_print_alignments(approx_alignments)


if __name__ == "__main__":
    execute_script()
