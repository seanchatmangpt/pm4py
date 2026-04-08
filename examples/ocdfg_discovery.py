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
from examples import examples_conf
import os
import importlib.util


def execute_script():
    ocel = pm4py.read_ocel(os.path.join("..", "tests", "input_data", "ocel", "example_log.jsonocel"))
    ocdfg = pm4py.discover_ocdfg(ocel)

    if importlib.util.find_spec("graphviz"):
        # views the model with the frequency annotation
        pm4py.view_ocdfg(ocdfg, format=examples_conf.TARGET_IMG_FORMAT)
        # views the model with the performance annotation
        pm4py.view_ocdfg(ocdfg, format=examples_conf.TARGET_IMG_FORMAT, annotation="performance", performance_aggregation="median")


if __name__ == "__main__":
    execute_script()
