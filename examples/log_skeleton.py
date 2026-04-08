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
from pm4py.algo.discovery.log_skeleton import algorithm as lsk
from pm4py.algo.conformance.log_skeleton import algorithm as lsk_conf
import os


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    # discovers the log skeleton with a minimal noise
    log_skeleton = lsk.apply(log, parameters={lsk.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: 0.01})
    print(log_skeleton)
    # applies conformance checking to it
    results = lsk_conf.apply(log, log_skeleton)
    for i in range(min(len(results), 5)):
        # print the i-the conformance checking
        print(results[i])


if __name__ == "__main__":
    execute_script()
