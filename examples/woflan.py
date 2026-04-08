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

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.analysis.woflan import algorithm as woflan
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    net, im, fm = alpha_miner.apply(log)
    is_sound, diagn = woflan.apply(net, im, fm, parameters={"print_diagnostics": True, "return_diagnostics": True})
    print("is_sound", is_sound)
    print(diagn)


if __name__ == "__main__":
    execute_script()
