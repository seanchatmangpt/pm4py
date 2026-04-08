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
from pm4py.algo.transformation.to_embeddings import algorithm as to_embeddings
from pm4py.util import constants


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")

    log_paid = to_embeddings.keep_top_k_per_similarity(log, "paid cases", 2, parameters={
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "concept:name"})
    print(log_paid)

    log_rejected = to_embeddings.keep_top_k_per_similarity(log, "rejected cases", 2, parameters={
        constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY: "concept:name"})
    print(log_rejected)


if __name__ == "__main__":
    execute_script()
