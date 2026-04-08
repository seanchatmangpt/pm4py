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


from pm4py.objects.bpmn.obj import BPMN
from typing import Optional, Dict, Any
from copy import deepcopy


def apply(bpmn_graph: BPMN, string_dictio: Dict[str, str], parameters: Optional[Dict[Any, Any]] = None) -> BPMN:
    if parameters is None:
        parameters = {}

    bpmn_graph = deepcopy(bpmn_graph)

    for node in bpmn_graph.get_nodes():
        if isinstance(node, BPMN.Task):
            name = node.get_name()
            if name in string_dictio:
                node.set_name(string_dictio[name])

    return bpmn_graph
