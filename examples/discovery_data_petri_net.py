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
from pm4py.algo.decision_mining import algorithm as decision_mining
from examples import examples_conf
import os
import importlib.util


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes")
    log = pm4py.read_xes(log_path)
    net, im, fm = pm4py.discover_petri_net_inductive(log)
    net, im, fm = decision_mining.create_data_petri_nets_with_decisions(log, net, im, fm)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
