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
import os


def execute_script():
    # reads a XES log
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    log = pm4py.format_dataframe(log)

    if importlib.util.find_spec("graphviz"):
        # generates the default dotted chart (timestamp on X-axis, case ID on Y-axis, activity as color)
        pm4py.view_dotted_chart(log, format=examples_conf.TARGET_IMG_FORMAT)
        # generates the dotted chart with the activity on the X-axis, the resource on the Y-axis, and the group
        # as color
        pm4py.view_dotted_chart(log, format=examples_conf.TARGET_IMG_FORMAT, attributes=["concept:name", "org:resource", "org:group"])


if __name__ == "__main__":
    execute_script()
