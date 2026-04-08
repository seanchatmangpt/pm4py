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

from copy import deepcopy

from pm4py.objects.log.obj import EventLog, Trace, Event


def execute_script():
    L = EventLog()
    e1 = Event()
    e1["concept:name"] = "A"
    e2 = Event()
    e2["concept:name"] = "B"
    e3 = Event()
    e3["concept:name"] = "C"
    e4 = Event()
    e4["concept:name"] = "D"
    t = Trace()
    t.append(e1)
    t.append(e2)
    t.append(e3)
    t.append(e4)
    for i in range(10000):
        L.append(deepcopy(t))
    print(len(L))


if __name__ == "__main__":
    execute_script()
