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
from pm4py.algo.transformation.log_to_target import algorithm as log_to_target


def execute_script():
    log = pm4py.read_xes("../tests/input_data/running-example.xes")
    rem_time_target, classes = log_to_target.apply(log, variant=log_to_target.Variants.REMAINING_TIME)
    print(rem_time_target)
    next_time_target, classes = log_to_target.apply(log, variant=log_to_target.Variants.NEXT_TIME)
    print(next_time_target)
    next_activity_target, next_activities = log_to_target.apply(log, variant=log_to_target.Variants.NEXT_ACTIVITY)
    print(next_activity_target)
    print(next_activities)


if __name__ == "__main__":
    execute_script()
