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
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from pm4py.objects.conversion.bpmn import converter as bpmn_converter


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    bpmn_graph = bpmn_importer.apply(os.path.join("..", "tests", "input_data", "running-example.bpmn"))
    net, im, fm = bpmn_converter.apply(bpmn_graph, variant=bpmn_converter.Variants.TO_PETRI_NET)
    precision_tbr = pm4py.precision_token_based_replay(log, net, im, fm)
    print("precision", precision_tbr)
    fitness_tbr = pm4py.precision_token_based_replay(log, net, im, fm)
    print("fitness", fitness_tbr)
    print(pm4py.check_soundness(net, im, fm))


if __name__ == "__main__":
    execute_script()
