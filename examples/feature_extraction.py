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
from pm4py.algo.transformation.log_to_features import algorithm as feature_extraction
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "running-example.xes"))
    data, feature_names = feature_extraction.apply(log, variant=feature_extraction.Variants.TRACE_BASED)
    print(data)
    print(feature_names)
    data, feature_names = feature_extraction.apply(log, variant=feature_extraction.Variants.EVENT_BASED)
    print(data)
    print(feature_names)


if __name__ == "__main__":
    execute_script()
