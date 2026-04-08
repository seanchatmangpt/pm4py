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


from typing import List, Tuple


def cycle_time(events: List[Tuple[float, float]], num_instances: int) -> float:
    """
    Computes the cycle time given a list of events (having a start and a complete timestamp)
    and the number of instances of the log

    The definition that has been followed is the one proposed in:
    https://www.presentationeze.com/presentations/lean-manufacturing-just-in-time/lean-manufacturing-just-in-time-full-details/process-cycle-time-analysis/calculate-cycle-time/#:~:text=Cycle%20time%20%3D%20Average%20time%20between,is%2024%20minutes%20on%20average.

    So:
    Cycle time  = Average time between completion of units.

    Example taken from the website:
    Consider a manufacturing facility, which is producing 100 units of product per 40 hour week.
    The average throughput rate is 1 unit per 0.4 hours, which is one unit every 24 minutes.
    Therefore the cycle time is 24 minutes on average.

    Parameters
    ---------------
    events
        List of events (each event is a tuple having the start and the complete timestamp)
    num_instances
        Number of instances of the log

    Returns
    ---------------
    cycle_time
        Cycle time
    """
    events = sorted(events, key=lambda x: (x[0], x[1]))

    st = events[0][0]
    et = events[0][1]

    production_time = 0

    for i in range(1, len(events)):
        this_st = events[i][0]
        this_et = events[i][1]

        if this_st > et:
            production_time += et - st
            st = this_st

        et = max(et, this_et)

    return production_time / num_instances
