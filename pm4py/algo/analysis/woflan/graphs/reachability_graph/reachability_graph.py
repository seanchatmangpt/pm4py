from pm4py.util import nx_utils
import numpy as np
from pm4py.algo.analysis.woflan.graphs import utility as helper


def apply(net, initial_marking, original_net=None):
    """
    Method that computes a reachability graph as networkx object
    :param net: Petri Net
    :param initial_marking: Initial Marking of the Petri Net
    :param original_net: Petri Net without short-circuited transition
    :return: Networkx Graph that represents the reachability graph of the Petri Net
    """
    initial_marking = helper.convert_marking(
        net, initial_marking, original_net
    )
    _, req_sparse, deltas, _, _ = helper.compute_firing_requirement(net)
    look_up_indices = {}
    j = 0
    reachability_graph = nx_utils.MultiDiGraph()
    reachability_graph.add_node(j, marking=initial_marking)

    working_set = set()
    working_set.add(j)

    look_up_indices[helper.marking_to_key(initial_marking)] = j

    j += 1
    while len(working_set) > 0:
        m = working_set.pop()
        possible_markings = helper.enabled_markings(
            req_sparse, deltas, reachability_graph.nodes[m]["marking"]
        )
        for marking in possible_markings:
            marking_key = helper.marking_to_key(marking[0])
            if marking_key not in look_up_indices:
                look_up_indices[marking_key] = j
                reachability_graph.add_node(j, marking=marking[0])
                working_set.add(j)
                reachability_graph.add_edge(m, j, transition=marking[1])
                j += 1
            else:
                reachability_graph.add_edge(
                    m,
                    look_up_indices[marking_key],
                    transition=marking[1],
                )
    return reachability_graph
