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
from pm4py.algo.transformation.log_to_interval_tree import algorithm as log_to_interval_tree


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    tree = log_to_interval_tree.apply(log, variant=log_to_interval_tree.Variants.OPEN_PATHS)
    # see how many paths are open at the timestamp 1319616410
    print(len(tree[1319616410]))
    # read the detailed information about the source and target event of each path
    print(tree[1319616410])

    # builds a new tree considering only the intervals going from an event with activity
    # 'T06 Determine necessity of stop advice'
    # to an event with activity 'T02 Check confirmation of receipt'
    tree = log_to_interval_tree.apply(log, variant=log_to_interval_tree.Variants.OPEN_PATHS, parameters={"filter_activity_couple": ("T06 Determine necessity of stop advice", "T02 Check confirmation of receipt")})
    # see how many paths are open at the timestamp 1319616410
    print(len(tree[1319616410]))
    # read the detailed information about the source and target event of each path
    print(tree[1319616410])


if __name__ == "__main__":
    execute_script()
