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


from pm4py.util import constants as pm4_constants

if pm4_constants.ENABLE_INTERNAL_IMPORTS:
    import importlib.util

    if importlib.util.find_spec("graphviz"):
        # imports the visualizations only if graphviz is installed
        from pm4py.visualization import (
            common,
            dfg,
            petri_net,
            process_tree,
            transition_system,
            bpmn,
            trie,
            ocel,
            network_analysis,
            heuristics_net
        )

        if importlib.util.find_spec("matplotlib"):
            from pm4py.visualization import performance_spectrum

            if importlib.util.find_spec("pyvis"):
                # SNA requires both packages matplotlib and pyvis.
                from pm4py.visualization import sna

    if importlib.util.find_spec("matplotlib"):
        # graphs require matplotlib. This is included in the default installation;
        # however, they may lead to problems in some platforms/deployments
        from pm4py.visualization import graphs
