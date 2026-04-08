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



from enum import Enum
from pm4py.objects.ocel.obj import OCEL
from typing import Optional, Dict, Any
from pm4py.util import exec_utils, nx_utils
from pm4py.algo.transformation.ocel.graphs import (
    object_interaction_graph,
    object_descendants_graph,
    object_inheritance_graph,
    object_cobirth_graph,
    object_codeath_graph,
)


class Parameters(Enum):
    INCLUDE_OBJ_INTERACTION_GRAPH = "include_obj_interaction_graph"
    INCLUDE_OBJ_DESCENDANTS_GRAPH = "include_obj_descendants_graph"
    INCLUDE_OBJ_INHERITANCE_GRAPH = "include_obj_inheritance_graph"
    INCLUDE_OBJ_COBIRTH_GRAPH = "include_obj_cobirth_graph"
    INCLUDE_OBJ_CODEATH_GRAPH = "include_obj_codeath_graph"


def apply(ocel: OCEL, parameters: Optional[Dict[Any, Any]] = None):
    """
    Converts the graphs of features extracted from an OCEL to a NetworkX DiGraph object

    Parameters
    --------------
    ocel
        Object-centric event log
    parameters
        Parameters of the algorithm, including:
        - Parameters.INCLUDE_OBJ_INTERACTION_GRAPH => includes the object interaction graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_DESCENDANTS_GRAPH => includes the object descendants graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_INHERITANCE_GRAPH => includes the object inheritance graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_COBIRTH_GRAPH => includes the object cobirth graph in the NX DiGraph
        - Parameters.INCLUDE_OBJ_CODEATH_GRAPH => includes the object codeath graph in the NX DiGraph

    Returns
    -------------
    G
        NetworkX DiGraph
    """
    if parameters is None:
        parameters = {}

    include_obj_interaction_graph = exec_utils.get_param_value(
        Parameters.INCLUDE_OBJ_INTERACTION_GRAPH, parameters, True
    )
    include_obj_descendants_graph = exec_utils.get_param_value(
        Parameters.INCLUDE_OBJ_DESCENDANTS_GRAPH, parameters, True
    )
    include_obj_inheritance_graph = exec_utils.get_param_value(
        Parameters.INCLUDE_OBJ_INHERITANCE_GRAPH, parameters, True
    )
    include_obj_cobirth_graph = exec_utils.get_param_value(
        Parameters.INCLUDE_OBJ_COBIRTH_GRAPH, parameters, True
    )
    include_obj_codeath_graph = exec_utils.get_param_value(
        Parameters.INCLUDE_OBJ_CODEATH_GRAPH, parameters, True
    )

    G = nx_utils.DiGraph()
    if include_obj_interaction_graph:
        interaction_graph = object_interaction_graph.apply(
            ocel, parameters=parameters
        )
        G.add_edges_from(interaction_graph, attr={"type": "INTERACTION"})

    if include_obj_descendants_graph:
        descendants_graph = object_descendants_graph.apply(
            ocel, parameters=parameters
        )
        G.add_edges_from(descendants_graph, attr={"type": "DESCENDANTS"})

    if include_obj_inheritance_graph:
        inheritance_graph = object_inheritance_graph.apply(
            ocel, parameters=parameters
        )
        G.add_edges_from(inheritance_graph, attr={"type": "INHERITANCE"})

    if include_obj_cobirth_graph:
        cobirth_graph = object_cobirth_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(cobirth_graph, attr={"type": "COBIRTH"})

    if include_obj_codeath_graph:
        codeath_graph = object_codeath_graph.apply(ocel, parameters=parameters)
        G.add_edges_from(codeath_graph, attr={"type": "CODEATH"})

    return G
