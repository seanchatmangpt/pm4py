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


import sys

import numpy as np

GS_SCORE = 1  # score has sensitivity of 1


def score(output_universes):
    return [x for x in np.flip(output_universes)]


def exp_mech(output_universes, epsilon):
    scores = score(output_universes)
    raw_prob = [np.exp((epsilon * x) / (2 * GS_SCORE)) for x in scores]
    i = 0
    for prob in raw_prob:
        if prob == float('inf'):
            raw_prob[i] = sys.float_info.max
        i += 1
    prob = np.exp(raw_prob - np.max(raw_prob))
    prob = prob / prob.sum()
    return np.random.choice(output_universes, p=prob)
