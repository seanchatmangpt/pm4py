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
from pm4py.algo.discovery.ocel.saw_nets import algorithm as saw_nets_disc
from pm4py.objects.petri_net.obj import Marking
from examples import examples_conf
import importlib.util


def execute_script():
    ocel = pm4py.read_ocel("../tests/input_data/ocel/ocel_order_simulated.csv")
    res = saw_nets_disc.apply(ocel)

    if importlib.util.find_spec("graphviz"):
        for ot in res["ot_saw_nets"]:
            pm4py.view_petri_net(res["ot_saw_nets"][ot], Marking(), Marking(), format=examples_conf.TARGET_IMG_FORMAT)
        pm4py.view_petri_net(res["multi_saw_net"], Marking(), Marking(), decorations=res["decorations_multi_saw_net"],
                             format=examples_conf.TARGET_IMG_FORMAT)


if __name__ == "__main__":
    execute_script()
