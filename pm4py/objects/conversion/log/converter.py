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


from enum import Enum

from pm4py.objects.conversion.log.variants import (
    to_event_stream,
    to_event_log,
    to_data_frame,
    to_nx,
)


class Variants(Enum):
    TO_EVENT_LOG = to_event_log
    TO_EVENT_STREAM = to_event_stream
    TO_DATA_FRAME = to_data_frame
    TO_NX = to_nx


TO_EVENT_LOG = Variants.TO_EVENT_LOG
TO_EVENT_STREAM = Variants.TO_EVENT_STREAM
TO_DATA_FRAME = Variants.TO_DATA_FRAME


def apply(log, parameters=None, variant=None):
    if variant is None:
        variant = Variants.TO_EVENT_LOG
    return variant.value.apply(log, parameters=parameters)
