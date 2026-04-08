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

from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.evaluation.precision import algorithm as etc_alg
from pm4py.objects.log.importer.xes import importer as xes_importer
from tests.constants import INPUT_DATA_DIR
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


class ETCTest(unittest.TestCase):
    def test_etc1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        log = xes_importer.apply(os.path.join(INPUT_DATA_DIR, "running-example.xes"))
        process_tree = inductive_miner.apply(log)
        net, marking, final_marking = process_tree_converter.apply(process_tree)
        precision = etc_alg.apply(log, net, marking, final_marking, variant=etc_alg.ETCONFORMANCE_TOKEN)
        del precision


if __name__ == "__main__":
    unittest.main()
