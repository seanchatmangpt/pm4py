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


from collections import defaultdict
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any, Tuple, Set


def apply(ocel: OCEL,
          parameters: Optional[Dict[Any,
                                    Any]] = None) -> Tuple[Set[str],
                                                           Dict[Tuple[str,
                                                                str,
                                                                str],
                                                                int]]:
    if parameters is None:
        parameters = {}

    import pm4py

    # Available graph types
    graph_types = [
        "object_interaction",
        "object_descendants",
        "object_inheritance",
        "object_cobirth",
        "object_codeath"
    ]

    # Initialize OTG components
    edges = defaultdict(int)

    object_types = set(ocel.objects["ocel:type"].unique())
    objects = ocel.objects.to_dict("records")
    objects = {x["ocel:oid"]: x["ocel:type"] for x in objects}

    # Iterate over each relationship type
    for sigma in graph_types:
        # Discover the object graph for the relationship type
        object_graph = pm4py.discover_objects_graph(ocel, graph_type=sigma)

        # Build the edges for the OTG
        for o1, o2 in object_graph:
            ot1 = objects[o1]
            ot2 = objects[o2]

            ot_pair = (ot1, ot2)

            edge = (ot_pair[0], sigma, ot_pair[1])
            edges[edge] += 1

    return object_types, dict(edges)
