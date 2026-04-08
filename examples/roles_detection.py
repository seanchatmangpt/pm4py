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
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.organizational_mining.roles import algorithm as roles_algorithm


def execute_script():
    # import the log
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"), variant="nonstandard")

    roles = roles_algorithm.apply(log)

    # print the results (grouped activities) on the screen
    print([x.activities for x in roles])


if __name__ == "__main__":
    execute_script()
