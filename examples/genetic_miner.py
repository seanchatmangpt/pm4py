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
import os
import importlib.util
from examples import examples_conf
from pm4py.algo.discovery.genetic.algorithm import Parameters


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = pm4py.discover_petri_net_genetic(log, population_size = 10, generations = 10)

    fitness_tbr = pm4py.fitness_token_based_replay(log, net, im, fm)
    print("fitness_tbr", fitness_tbr)
    precision_tbr = pm4py.precision_token_based_replay(log, net, im, fm)
    print("precision_tbr", precision_tbr)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
