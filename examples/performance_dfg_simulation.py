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
from pm4py.algo.simulation.playout.dfg import algorithm as dfg_simulator


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    frequency_dfg, sa, ea = pm4py.discover_dfg(log)
    performance_dfg, sa, ea = pm4py.discover_performance_dfg(log)
    simulated_log = dfg_simulator.apply(frequency_dfg, sa, ea, variant=dfg_simulator.Variants.PERFORMANCE,
                                        parameters={"performance_dfg": performance_dfg})
    print(simulated_log)


if __name__ == "__main__":
    execute_script()
