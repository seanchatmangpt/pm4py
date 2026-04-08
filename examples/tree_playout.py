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
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.simulation.playout.process_tree import algorithm as tree_playout
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    tree = inductive_miner.apply(log)
    new_log_1 = tree_playout.apply(tree)
    print(len(new_log_1))
    new_tree_1 = inductive_miner.apply(new_log_1)
    print(new_tree_1)
    new_log_2 = tree_playout.apply(tree, variant=tree_playout.Variants.EXTENSIVE)
    print(len(new_log_2))
    new_tree_2 = inductive_miner.apply(new_log_2)
    print(new_tree_2)


if __name__ == "__main__":
    execute_script()
