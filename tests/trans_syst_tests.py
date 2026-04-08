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
from tests.constants import INPUT_DATA_DIR
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.transition_system import algorithm as ts_alg
import unittest
import os


class TransitionSystemTest(unittest.TestCase):
    def test_transitionsystem1(self):
        # to avoid static method warnings in tests,
        # that by construction of the unittest package have to be expressed in such way
        self.dummy_variable = "dummy_value"
        input_log = os.path.join(INPUT_DATA_DIR, "running-example.xes")
        log = xes_importer.apply(input_log)
        ts = ts_alg.apply(log, parameters={
            ts_alg.Variants.VIEW_BASED.value.Parameters.PARAM_KEY_VIEW: ts_alg.Variants.VIEW_BASED.value.Parameters.VIEW_SEQUENCE,
            ts_alg.Variants.VIEW_BASED.value.Parameters.PARAM_KEY_WINDOW: 3,
            ts_alg.Variants.VIEW_BASED.value.Parameters.PARAM_KEY_DIRECTION: ts_alg.Variants.VIEW_BASED.value.Parameters.DIRECTION_FORWARD})
        viz = pm4py.visualization.transition_system.util.visualize_graphviz.visualize(ts)
        del viz


if __name__ == "__main__":
    unittest.main()
