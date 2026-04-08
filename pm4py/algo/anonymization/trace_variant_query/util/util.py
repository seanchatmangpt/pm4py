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



import datetime

from dateutil.tz import tzutc

from pm4py.objects.log import obj

TRACE_START = "TRACE_START"
TRACE_END = "TRACE_END"
EVENT_DELIMETER = ">>>"


def generate_pm4py_log(trace_frequencies):
    log = obj.EventLog()
    trace_count = 0
    for variant in trace_frequencies.items():
        frequency = variant[1]
        activities = variant[0].split(EVENT_DELIMETER)
        for i in range(0, frequency):
            trace = obj.Trace()
            trace.attributes["concept:name"] = trace_count
            trace_count = trace_count + 1
            for activity in activities:
                if not TRACE_END in activity:
                    event = obj.Event()
                    event["concept:name"] = str(activity)
                    event["time:timestamp"] = datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=tzutc())
                    trace.append(event)
            log.append(trace)
    return log
