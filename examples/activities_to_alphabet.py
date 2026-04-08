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
from pm4py.objects.log.util import activities_to_alphabet
from pm4py.util import constants


def execute_script():
    dataframe = pm4py.read_xes("../tests/input_data/running-example.xes", return_legacy_log_object=False)
    renamed_dataframe = activities_to_alphabet.apply(dataframe, parameters={constants.PARAMETER_CONSTANT_ACTIVITY_KEY: "concept:name"})
    print(renamed_dataframe)


if __name__ == "__main__":
    execute_script()
