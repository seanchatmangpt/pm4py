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
from pm4py.algo.discovery.transition_system import algorithm as ts_discovery
from examples import examples_conf
import os
import importlib.util


def execute_script():
    # log_path = "C:/Users/bas/Documents/tue/svn/private/logs/ilp_test_2_abcd_acbd.xes"
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    log = xes_importer.apply(log_path)
    ts = ts_discovery.apply(log, parameters={"include_data": True})

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.transition_system import visualizer as ts_vis
        viz = ts_vis.apply(ts, parameters={ts_vis.Variants.VIEW_BASED.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        ts_vis.view(viz)

    for state in ts.states:
        print(state.name, "ingoing=", len(state.data["ingoing_events"]), "outgoing=",
              len(state.data["outgoing_events"]))
    for trans in ts.transitions:
        print(trans.name, trans.from_state.name, trans.to_state.name, "frequency=", len(trans.data["events"]))


if __name__ == '__main__':
    execute_script()
