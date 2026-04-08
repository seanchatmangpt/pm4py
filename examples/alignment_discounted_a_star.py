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
import time
from pm4py.algo.conformance.alignments.petri_net import algorithm as ali
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as petri_importer


def synchronous_discounted_alignment():
    '''
    This function runs an alignment based on the discounted edit distance
    By using the synchronous product
    :return:
    '''
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    # to see the net :
    #vizu(net,marking,fmarking).view()

    start=time.time()

    alignments1 = ali.apply(log._list[0], net, marking, fmarking,
                            variant=ali.VERSION_DISCOUNTED_A_STAR,
                            parameters={ali.Parameters.SYNCHRONOUS:True,ali.Parameters.EXPONENT:1.1})
    print(alignments1)
    print("Time:",(time.time()-start))

def no_synchronous_discounted_alignment():
    '''
    This function runs an alignment based on the discounted edit distance
    By using the Petri net and petri_net.utils.align_utils.discountedEditDistance function
    '''
    log_path = os.path.join("..", "tests", "input_data", "running-example.xes")
    pnml_path = os.path.join("..", "tests", "input_data", "running-example.pnml")
    log = xes_importer.apply(log_path)
    net, marking, fmarking = petri_importer.apply(pnml_path)

    start=time.time()

    alignments1 = ali.apply(log._list[0], net, marking, fmarking,
                            variant=ali.VERSION_DISCOUNTED_A_STAR,
                            parameters={ali.Parameters.SYNCHRONOUS:False,ali.Parameters.EXPONENT:1.1})
    print(alignments1)
    print("Time:",(time.time()-start))


def execute_script():
    synchronous_discounted_alignment()
    no_synchronous_discounted_alignment()


if __name__ == '__main__':
    execute_script()
