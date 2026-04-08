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
import importlib.util


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")

    powl_model = pm4py.discover_powl(log)
    # get the __repr__ of the POWL model
    powl_string = str(powl_model)
    print(powl_model)

    # parse the same string into a new POWL model
    powl_model2 = pm4py.parse_powl_model_string(powl_string)
    # see that the __repr__ of the two models are the same (same length)
    powl_string2 = str(powl_model2)
    print(powl_string2)
    print(len(powl_string), len(powl_string2))

    if importlib.util.find_spec("graphviz"):
        # represents the parsed model on the screen
        pm4py.view_powl(powl_model2, format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
