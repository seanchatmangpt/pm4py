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

import pm4py
from pm4py.algo.transformation.log_to_features.util import locally_linear_embedding
from examples import examples_conf
import importlib.util


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))

    if importlib.util.find_spec("scipy") and importlib.util.find_spec("sklearn"):
        # calculates the graph:
        # values of y more distant from 0 signal executions that differ from the mainstream behavior
        x, y = locally_linear_embedding.apply(log)

        if importlib.util.find_spec("matplotlib") and importlib.util.find_spec("graphviz"):
            from pm4py.visualization.graphs import visualizer
            gviz = visualizer.apply(x, y, variant=visualizer.Variants.DATES,
                                    parameters={"title": "Locally Linear Embedding", "format": examples_conf.TARGET_IMG_FORMAT, "y_axis": "Intensity"})
            visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
