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

import time

import pm4py
from pm4py.objects.log.util import filtering_utils


def execute_script():
    log = pm4py.read_xes("../tests/compressed_input_data/02_teleclaims.xes.gz")
    tree = pm4py.discover_process_tree_inductive(log, noise_threshold=0.3)
    net, im, fm = pm4py.convert_to_petri_net(tree)
    # reduce the log to one trace per variant
    log = filtering_utils.keep_one_trace_per_variant(log)
    for index, trace in enumerate(log):
        print(index)
        aa = time.time()
        check_tree = pm4py.check_is_fitting(trace, tree)
        bb = time.time()
        check_petri = pm4py.check_is_fitting(trace, net, im, fm)
        cc = time.time()
        print("check on tree: ", check_tree, "time", bb - aa)
        print("check on Petri net: ", check_petri, "time", cc - bb)
        print()


if __name__ == "__main__":
    execute_script()
