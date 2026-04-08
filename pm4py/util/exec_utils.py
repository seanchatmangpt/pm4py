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


def unroll(value):
    if isinstance(value, Enum):
        return value.value
    return value


# this function can be moved to a util when string values of the
# parameters are no longer supported. (or is no longer needed ;-))
def get_param_value(p, parameters, default):
    if parameters is None:
        return unroll(default)
    unrolled_parameters = {}
    for p0 in parameters:
        unrolled_parameters[unroll(p0)] = parameters[p0]
    if p in parameters:
        val = parameters[p]
        return unroll(val)
    up = unroll(p)
    if up in unrolled_parameters:
        val = unrolled_parameters[up]
        return unroll(val)
    return unroll(default)


def get_variant(variant):
    if isinstance(variant, Enum):
        return variant.value
    return variant
