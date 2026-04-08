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

import unittest

import pm4py


class DfgTests(unittest.TestCase):
    def test_filter_act_percentage(self):
        from pm4py.algo.filtering.dfg import dfg_filtering
        log = pm4py.read_xes("input_data/running-example.xes")
        dfg, sa, ea = pm4py.discover_dfg(log)
        act_count = pm4py.get_event_attribute_values(log, "concept:name")
        dfg_filtering.filter_dfg_on_activities_percentage(dfg, sa, ea, act_count, 0.1)

    def test_filter_paths_percentage(self):
        from pm4py.algo.filtering.dfg import dfg_filtering
        log = pm4py.read_xes("input_data/running-example.xes")
        dfg, sa, ea = pm4py.discover_dfg(log)
        act_count = pm4py.get_event_attribute_values(log, "concept:name")
        dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, act_count, 0.3)


if __name__ == "__main__":
    unittest.main()
