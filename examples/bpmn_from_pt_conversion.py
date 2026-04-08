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
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
from examples import examples_conf
import importlib.util



def execute_script():
    log_path = os.path.join(os.path.join("..", "tests", "input_data", "running-example.xes"))
    log = xes_import.apply(log_path)
    ptree = inductive_miner.apply(log)
    bpmn = pt_converter.apply(ptree, variant=pt_converter.Variants.TO_BPMN)

    if importlib.util.find_spec("graphviz"):
        bpmn_exporter.apply(bpmn, "stru.bpmn")
        os.remove("stru.bpmn")
        pm4py.view_bpmn(bpmn, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
