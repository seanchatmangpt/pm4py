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


from pm4py.objects.log.obj import EventLog


def insert_event_index_as_event_attribute(
    stream, event_index_attr_name="@@eventindex"
):
    """
    Insert the current event index as event attribute

    Parameters
    -----------
    stream
        Stream
    event_index_attr_name
        Attribute name given to the event index
    """

    if not type(stream) is EventLog:
        for i in range(0, len(stream._list)):
            stream._list[i][event_index_attr_name] = i + 1

    return stream


def insert_trace_index_as_event_attribute(
    log, trace_index_attr_name="@@traceindex"
):
    """
    Inserts the current trace index as event attribute
    (overrides previous values if needed)

    Parameters
    -----------
    log
        Log
    trace_index_attr_name
        Attribute name given to the trace index
    """
    for i in range(len(log._list)):
        for j in range(len(log._list[i])):
            log._list[i][j][trace_index_attr_name] = i + 1

    return log
