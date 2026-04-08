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


from enum import Enum, auto
from collections import Counter
from pm4py.algo.discovery.inductive.dtypes.im_ds import IMDataStructureUVCL


class FilteringType(Enum):
    DYNAMIC = auto()
    DECREASING_FACTOR = auto()


DEFAULT_FILTERING_TYPE = FilteringType.DECREASING_FACTOR
FILTERING_THRESHOLD = "filtering_threshold"
FILTERING_TYPE = "filtering_type"


def filter_most_frequent_variants(log):
    to_remove_freq = min([freq for var, freq in log.items()])
    new_log = Counter()
    for var, freq in log.items():
        if freq == to_remove_freq:
            continue
        new_log[var] = freq

    return IMDataStructureUVCL(new_log)


def filter_most_frequent_variants_with_decreasing_factor(
    log, decreasing_factor
):
    sorted_variants = sorted(log, key=log.get, reverse=True)
    new_log = Counter()

    already_added_sum = 0
    prev_var_count = -1

    for variant in sorted_variants:
        frequency = log[variant]
        if (
            already_added_sum == 0
            or frequency > decreasing_factor * prev_var_count
        ):
            new_log[variant] = frequency
            already_added_sum = already_added_sum + frequency
            prev_var_count = frequency
        else:
            break

    return IMDataStructureUVCL(new_log)
