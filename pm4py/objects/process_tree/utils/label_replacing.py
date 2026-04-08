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


from pm4py.objects.process_tree.obj import ProcessTree
from typing import Optional, Dict, Any
from copy import deepcopy


def apply(process_tree: ProcessTree, string_dictio: Dict[str, str], rec_depth=0, parameters: Optional[Dict[Any, Any]] = None) -> ProcessTree:
    """
    Replaces the labels in the given process tree using the provided dictionary.

    Parameters
    -----------------
    process_tree
        Process tree
    string_dictio
        Correspondence dictionary (old labels -> new labels)

    Returns
    -----------------
    revised_tree
        Revised process tree
    """
    if parameters is None:
        parameters = {}

    if rec_depth == 0:
        process_tree = deepcopy(process_tree)

    if process_tree.label is not None and process_tree.label in string_dictio:
        process_tree.label = string_dictio[process_tree.label]

    for child in process_tree.children:
        apply(child, string_dictio, rec_depth=rec_depth+1, parameters=parameters)

    return process_tree
