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
from pm4py.statistics.overlap.interval_events.log import get as interval_events_overlap
import os


def execute_script():
    log = pm4py.read_xes(os.path.join("..", "tests", "input_data", "interval_event_log.xes"))
    # gets the overlap of each interval event with the other events of the log
    overlap = interval_events_overlap.apply(log, parameters={
        interval_events_overlap.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})
    # print the overlap for all the events
    print(overlap)
    # print the number of intersections of the event having max overlap
    print(max(overlap))


if __name__ == "__main__":
    execute_script()
