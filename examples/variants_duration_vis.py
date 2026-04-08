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
from pm4py.visualization.variants_duration import visualizer


def execute_script():
    log = pm4py.read_xes("../tests/input_data/receipt.xes")

    # visualize the variants durations aligning on the start
    gviz = visualizer.apply(log, parameters={"format": "svg", "alignment_criteria": "start"})
    visualizer.view(gviz)

    # visualize the variants durations aligning on the end
    gviz = visualizer.apply(log, parameters={"format": "svg", "alignment_criteria": "end"})
    visualizer.view(gviz)

    # visualize the variants aligning on (the first occurrence of) a given activity
    gviz = visualizer.apply(log, parameters={"format": "svg", "alignment_criteria": "T02 Check confirmation of receipt", "max_variants": 10})
    visualizer.view(gviz)


if __name__ == "__main__":
    execute_script()
