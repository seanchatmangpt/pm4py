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
from pm4py.algo.evaluation import algorithm as general_evaluation
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "reviewing.xes"))
    process_tree = inductive_miner.apply(log)
    net, marking, final_marking = process_tree_converter.apply(process_tree)
    metrics = general_evaluation.apply(log, net, marking, final_marking)
    print("metrics=", metrics)


if __name__ == "__main__":
    execute_script()
