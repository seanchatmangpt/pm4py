
from typing import Set



def pre_set(occn, activity: str, object_type: str = None) -> Set:
    """
    Returns the set of predecessor activities for a given activity in an object-centric causal net.
    Restricted to predecessors connected using arcs of the specified object type, if provided.

    Parameters
    ----------
    occn : OCCausalNet
        The object-centric causal net to query
    activity : str
        The name of the activity for which to get the predecessors
    object_type : str, optional
        The object type to restrict the predecessors to (default is None)

    Returns
    -------
    Set
        Set of predecessor activities of the specified object type.
    """
    if activity not in occn.activities:
        return set()

    dg = occn.dependency_graph

    if object_type is None:
        return dg.predecessors(activity)

    return {
        predecessor
        for predecessor, _, edge_key in dg.in_edges(activity, keys=True)
        if edge_key == object_type
    }

def post_set(occn, activity: str, object_type: str = None) -> Set:
    """
    Returns the set of successor activities for a given activity in an object-centric causal net.
    Restricted to successors connected using arcs of the specified object type, if provided.

    Parameters
    ----------
    occn : OCCausalNet
        The object-centric causal net to query
    activity : str
        The name of the activity for which to get the successors
    object_type : str, optional
        The object type to restrict the successors to (default is None)

    Returns
    -------
    Set
        Set of successor activities of the specified object type.
    """
    if activity not in occn.activities:
        return set()

    dg = occn.dependency_graph

    if object_type is None:
        return dg.successors(activity)

    return {
        successor
        for _, successor, edge_key in dg.out_edges(activity, keys=True)
        if edge_key == object_type
    }



