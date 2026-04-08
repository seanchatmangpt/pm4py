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
import sys


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/example_log.jsonocel")
    print(ocel)
    # filters the connected components of the OCEL in which there is at least a delivery,
    # obtaining a filtered OCEL back.
    ocel_with_del = pm4py.filter_ocel_cc_otype(ocel, "delivery")
    print(ocel_with_del)
    # filters the connected components of the OCEL with at least five different objects,
    # obtaining a filtered OCEL back.
    ocel_with_three_objs = pm4py.filter_ocel_cc_length(ocel, 5, sys.maxsize)
    print(ocel_with_three_objs)


if __name__ == "__main__":
    execute_script()
