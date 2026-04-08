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


from pm4py.objects.log.obj import EventLog, Trace, Event
from copy import copy


def keep_one_trace_per_variant(log, parameters=None):
    """
    Keeps only one trace per variant (does not matter for basic inductive miner)

    Parameters
    --------------
    log
        Log
    parameters
        Parameters of the algorithm

    Returns
    --------------
    new_log
        Log (with one trace per variant)
    """
    if parameters is None:
        parameters = {}

    from pm4py.statistics.variants.log import get as variants_module

    new_log = EventLog()
    if log is not None:
        variants = variants_module.get_variants(log, parameters=parameters)
        for var in variants:
            curr_trace = variants[var][0]
            new_trace = Trace(attributes=copy(curr_trace.attributes))
            new_trace.attributes["@@num_traces"] = len(variants[var])
            for ev in curr_trace:
                new_trace.append(ev)
            new_log.append(new_trace)

    return new_log


def keep_only_one_attribute_per_event(log, attribute_key):
    """
    Keeps only one attribute per event

    Parameters
    ---------------
    log
        Event log
    attribute_key
        Attribute key
    """
    new_log = EventLog()
    if log is not None:
        for trace in log:
            new_trace = Trace()
            for ev in trace:
                new_trace.append(Event({attribute_key: ev[attribute_key]}))
            new_log.append(new_trace)

    return new_log
