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
import unittest
import pm4py
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.objects.conversion.process_tree import converter as tree_converter
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from pm4py.objects.bpmn.layout import layouter as bpmn_layouter
from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter


class BPMNTests(unittest.TestCase):
    def test_tree_to_bpmn(self):
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        tree = pm4py.discover_process_tree_inductive(log)
        bpmn_graph = tree_converter.apply(tree, variant=tree_converter.Variants.TO_BPMN)

    def test_bpmn_to_petri_net(self):
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        bpmn_graph = bpmn_importer.apply(os.path.join("input_data", "running-example.bpmn"))
        net, im, fm = bpmn_converter.apply(bpmn_graph, variant=bpmn_converter.Variants.TO_PETRI_NET)
        fitness_tbr = pm4py.fitness_token_based_replay(log, net, im, fm)

    def test_bpmn_layouting(self):
        log = pm4py.read_xes(os.path.join("input_data", "running-example.xes"))
        tree = pm4py.discover_process_tree_inductive(log)
        bpmn_graph = tree_converter.apply(tree, variant=tree_converter.Variants.TO_BPMN)
        bpmn_graph = bpmn_layouter.apply(bpmn_graph)

    def test_bpmn_exporting(self):
        bpmn_graph = bpmn_importer.apply(os.path.join("input_data", "running-example.bpmn"))
        bpmn_exporter.apply(bpmn_graph, os.path.join("test_output_data", "running-example.bpmn"))
        os.remove(os.path.join("test_output_data", "running-example.bpmn"))

    def test_bpmn_importing_and_layouting(self):
        bpmn_graph = bpmn_importer.apply(os.path.join("input_data", "running-example.bpmn"))
        bpmn_graph = bpmn_layouter.apply(bpmn_graph)


if __name__ == "__main__":
    unittest.main()
