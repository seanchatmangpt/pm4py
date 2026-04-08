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


from pm4py.streaming.importer.xes.variants import (
    xes_trace_stream,
    xes_event_stream,
)
from enum import Enum
from pm4py.util import exec_utils


class Variants(Enum):
    XES_EVENT_STREAM = xes_event_stream
    XES_TRACE_STREAM = xes_trace_stream


DEFAULT_VARIANT = Variants.XES_EVENT_STREAM


def apply(path, variant=DEFAULT_VARIANT, parameters=None):
    """
    Imports a stream from a XES log

    Parameters
    ---------------
    path
        Path to the XES log
    variant
        Variant of the importer:
         - Variants.XES_EVENT_STREAM
         - Variants.XES_TRACE_STREAM

    Returns
    ---------------
    streaming_reader
        Streaming XES reader
    """
    return exec_utils.get_variant(variant).apply(path, parameters=parameters)
