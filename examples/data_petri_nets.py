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

import os

import pm4py
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.petri_net.data_petri_nets import semantics
from pm4py.objects.petri_net.data_petri_nets.data_marking import DataMarking
from pm4py.objects.log.importer.xes import importer as xes_importer
from examples import examples_conf
import importlib.util


def get_trans_by_name(net, name):
    ret = [x for x in net.transitions if x.name == name]
    if len(ret) == 0:
        return None
    return ret[0]


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "roadtraffic100traces.xes"))
    net, im, fm = pm4py.read_pnml(os.path.join("..", "tests", "input_data", "data_petri_net.pnml"), auto_guess_final_marking=True)

    if importlib.util.find_spec("graphviz"):
        pm4py.view_petri_net(net, im, fm, format=examples_conf.TARGET_IMG_FORMAT)

    aligned_traces = alignments.apply(log, net, im, fm, variant=alignments.Variants.VERSION_DIJKSTRA_LESS_MEMORY, parameters={"ret_tuple_as_trans_desc": True})
    for index, trace in enumerate(log):
        aligned_trace = aligned_traces[index]
        al = [(x[0][0], get_trans_by_name(net, x[0][1])) for x in aligned_trace["alignment"]]
        m = DataMarking(im)
        idx = 0
        for el in al:
            if el[1] is not None:
                en_t = semantics.enabled_transitions(net, m, trace[min(idx, len(trace) - 1)])
                if el[1] in en_t:
                    if "guard" in el[1].properties:
                        print(el[1], "GUARD SATISFIED", el[1].properties["guard"], m)
                    m = semantics.execute(el[1], net, m, trace[min(idx, len(trace) - 1)])
                else:
                    print("TRANSITION UNAVAILABLE! Guards are blocking")
            if el[0] != ">>":
                idx = idx + 1


if __name__ == "__main__":
    execute_script()
