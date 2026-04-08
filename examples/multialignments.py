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
from pm4py.algo.conformance.multialignments.variants.discounted_a_star import apply as multii
from pm4py.algo.conformance.multialignments.algorithm import Parameters
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer


def execute_script():
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    THETA = 1.1
    MU =  20
    multiali = multii(log,net,marking,fmarking, parameters={Parameters.EXPONENT:THETA, Parameters.MARKING_LIMIT:MU})
    print("Multi-alignment:",multiali['multi-alignment'])
    print("Maximal Levenshtein Edit Distance to Log:", multiali['max_distance_to_log'])


if __name__ == '__main__':
    execute_script()
