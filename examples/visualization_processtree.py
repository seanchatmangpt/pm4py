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

from pm4py.objects.log.importer.xes import importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from examples import examples_conf
import os
import importlib.util


def execute_script():
    log = importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    tree = inductive_miner.apply(log)

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.process_tree import visualizer as pt_vis_factory
        from pm4py.visualization.process_tree import visualizer as pt_visualizer

        gviz1 = pt_vis_factory.apply(tree, parameters={"format": examples_conf.TARGET_IMG_FORMAT})
        # pt_vis_factory.view(gviz1)
        gviz2 = pt_visualizer.apply(tree, parameters={pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        pt_visualizer.view(gviz2)


if __name__ == "__main__":
    execute_script()
