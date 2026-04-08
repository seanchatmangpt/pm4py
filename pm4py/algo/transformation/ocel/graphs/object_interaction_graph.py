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


from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Set, Tuple


def apply(
    ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None
) -> Set[Tuple[str, str]]:
    """
    Calculates the object interaction graph. Two objects are connected iff they are both related to an event
    of the OCEL.

    Parameters
    -----------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm

    Returns
    -----------------
    object_interaction_graph
        Object interaction graph (as set of tuples; undirected)
    """
    if parameters is None:
        parameters = {}

    graph = set()

    ev_rel_obj = (
        ocel.relations.groupby(ocel.event_id_column)[ocel.object_id_column]
        .agg(list)
        .to_dict()
    )

    for ev in ev_rel_obj:
        rel_obj = ev_rel_obj[ev]
        for o1 in rel_obj:
            for o2 in rel_obj:
                if o1 < o2:
                    graph.add((o1, o2))

    return graph
