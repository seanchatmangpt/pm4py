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


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "receipt.xes"))
    temporal_features = pm4py.extract_temporal_features_dataframe(log, grouper_freq="W")
    print(temporal_features)


if __name__ == "__main__":
    execute_script()
