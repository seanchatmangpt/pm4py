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

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.organizational_mining.sna import algorithm as sna_algorithm
from examples import examples_conf
import importlib.util


def execute_script():
    log = xes_importer.apply(os.path.join("..", "tests", "input_data", "running-example.xes"))

    hw_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.HANDOVER_LOG)
    wt_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.WORKING_TOGETHER_LOG)
    sub_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.SUBCONTRACTING_LOG)
    ja_values = sna_algorithm.apply(log, variant=sna_algorithm.Variants.JOINTACTIVITIES_LOG)

    if importlib.util.find_spec("graphviz") and importlib.util.find_spec("pyvis") and importlib.util.find_spec("networkx"):
        from pm4py.visualization.sna import visualizer as pn_vis
        gviz_sub = pn_vis.apply(sub_values, variant=pn_vis.Variants.NETWORKX,
                                parameters={pn_vis.Variants.NETWORKX.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        gviz_hw = pn_vis.apply(hw_values, variant=pn_vis.Variants.PYVIS)
        gviz_wt = pn_vis.apply(wt_values, variant=pn_vis.Variants.NETWORKX,
                               parameters={pn_vis.Variants.NETWORKX.value.Parameters.FORMAT: examples_conf.TARGET_IMG_FORMAT})
        gviz_ja = pn_vis.apply(ja_values, variant=pn_vis.Variants.PYVIS)
        pn_vis.view(gviz_sub, variant=pn_vis.Variants.NETWORKX)
        pn_vis.view(gviz_hw, variant=pn_vis.Variants.PYVIS)
        pn_vis.view(gviz_wt, variant=pn_vis.Variants.NETWORKX)
        pn_vis.view(gviz_ja, variant=pn_vis.Variants.PYVIS)


if __name__ == "__main__":
    execute_script()
