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
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.analysis.marking_equation import algorithm as marking_equation
from pm4py.algo.analysis.extended_marking_equation import algorithm as extended_marking_equation
from pm4py.objects.conversion.process_tree import converter as process_tree_converter
import os
from pm4py.objects.log.importer.xes import importer as xes_importer



def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "receipt.xes"))
    process_tree = inductive_miner.apply(log)
    net, im, fm = process_tree_converter.apply(process_tree)
    idx = 0
    # try to resolve the marking equation to find an heuristics and possible a vector of transitions
    # leading from im to fm
    sync_net, sync_im, sync_fm = pm4py.construct_synchronous_product_net(log[idx], net, im, fm)
    me_solver = marking_equation.build(sync_net, sync_im, sync_fm)
    h, x = me_solver.solve()
    firing_sequence, reach_fm1, explained_events = me_solver.get_firing_sequence(x)
    print("for trace at index "+str(idx)+": marking equation h = ", h)
    print("x vector reaches fm = ", reach_fm1)
    print("firing sequence = ", firing_sequence)
    # it fails and the value of heuristics is low
    #
    # now let's try with extended marking equation to find the heuristics and the vector!
    eme_solver = extended_marking_equation.build(log[idx], sync_net, sync_im, sync_fm)
    h, x = eme_solver.solve()
    # the heuristics is much better
    firing_sequence, reach_fm2, explained_events = eme_solver.get_firing_sequence(x)
    print("for trace at index "+str(idx)+": extended marking equation h = ", h)
    print("x vector reaches fm = ", reach_fm2)
    print("firing sequence = ", firing_sequence)


if __name__ == "__main__":
    execute_script()
