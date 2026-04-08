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

import pm4py
import os
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.algo.conformance.alignments.petri_net.utils import log_enrichment
from pm4py.objects.log.importer.xes import importer as xes_importer


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))
    filtered_log = pm4py.filter_variants_top_k(log, 1)
    net, im, fm = pm4py.discover_petri_net_inductive(filtered_log)
    aligned_traces = alignments.apply(log, net, im, fm, parameters={"ret_tuple_as_trans_desc": True})
    enriched_log = log_enrichment.apply(log, aligned_traces)
    print(enriched_log)


if __name__ == "__main__":
    execute_script()
