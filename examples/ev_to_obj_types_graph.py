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
    ocel = pm4py.read_ocel('../tests/input_data/ocel/example_log.jsonocel')

    if importlib.util.find_spec("graphviz"):
        from pm4py.visualization.ocel.eve_to_obj_types import visualizer
        gviz = visualizer.apply(ocel, parameters={"format": examples_conf.TARGET_IMG_FORMAT, "annotate_frequency": True})
        visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
