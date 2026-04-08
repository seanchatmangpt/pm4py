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

from pm4py.objects.log.importer.xes import importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
import memory_profiler
import time
import os
from pm4py.objects.conversion.process_tree import converter as process_tree_converter


class Shared:
    log = importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    process_tree = inductive_miner.apply(log)
    net, im, fm = process_tree_converter.apply(process_tree)


def nothing():
    time.sleep(3)


def f():
    aa = time.time()
    aligned_traces = alignments.apply(Shared.log, Shared.net, Shared.im, Shared.fm,
                                      variant=alignments.Variants.VERSION_DIJKSTRA_LESS_MEMORY)
    bb = time.time()
    print(bb - aa)


def g():
    aa = time.time()
    aligned_traces = alignments.apply(Shared.log, Shared.net, Shared.im, Shared.fm,
                                      variant=alignments.Variants.VERSION_DIJKSTRA_NO_HEURISTICS)
    bb = time.time()
    print(bb - aa)


if __name__ == "__main__":
    memory_usage = memory_profiler.memory_usage(nothing)
    nothing = max(memory_usage)
    print(nothing)
    memory_usage = memory_profiler.memory_usage(f)
    print(memory_usage)
    print(max(memory_usage) - nothing)
    memory_usage = memory_profiler.memory_usage(g)
    print(memory_usage)
    print(max(memory_usage) - nothing)
