"""
POWL 2.0 Choice Graph Discovery Algorithms.

Implements the discovery algorithms from:
H Kourani, G Park, WMP van der Aalst. "Unlocking Non-Block-Structured Decisions:
Inductive Mining with Choice Graphs" arXiv preprint arXiv:2505.07052.

Key components:
- MineDG: Generate candidate partition for choice graph cut
- Valid choice graph cut detection (Definition 5)
- Projection operation (Definition 6)
- Language semantics (Definition 3)
"""

from typing import Dict, List, Set, Tuple, Optional, Any
from collections.abc import Iterable
from dataclasses import dataclass

from pm4py.objects.powl.obj import DecisionGraph, POWL, Transition
from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.log.obj import EventLog, Trace


@dataclass
class ChoiceGraphCut:
    """
    A choice graph cut over an event log (Definition 4).

    Attributes:
        parts: List of activity subsets (partition of ΣL)
        choice_graph: Choice graph over the parts
    """
    parts: List[Set[str]]
    choice_graph: Optional[DecisionGraph] = None

    def __len__(self) -> int:
        """Return number of parts in the partition."""
        return len(self.parts)

    def __iter__(self):
        """Iterate over parts."""
        return iter(self.parts)


def compute_dfg(log: EventLog) -> Dict[Tuple[str, str], int]:
    """
    Compute the Directly-Follows Graph (DFG) from an event log.

    Args:
        log: Event log

    Returns:
        Dictionary mapping (activity, activity) to frequency
    """
    dfg = {}
    for trace in log:
        for i in range(len(trace) - 1):
            a = trace[i]['concept:name']
            b = trace[i + 1]['concept:name']
            dfg[(a, b)] = dfg.get((a, b), 0) + 1
    return dfg


def compute_dfg_relation(log: EventLog) -> Set[Tuple[str, str]]:
    """
    Compute the DFG relation (7→) from an event log.

    Args:
        log: Event log

    Returns:
        Set of directly-follows pairs
    """
    return set(compute_dfg(log).keys())


def compute_transitive_closure(dfg: Set[Tuple[str, str]]) -> Set[Tuple[str, str]]:
    """
    Compute the transitive closure (7→+) of the DFG relation.

    Args:
        dfg: DFG relation

    Returns:
        Transitive closure of the relation
    """
    closure = set(dfg)
    changed = True
    while changed:
        changed = False
        new_pairs = set()
        for (a, b) in closure:
            for (c, d) in closure:
                if b == c and (a, d) not in closure:
                    new_pairs.add((a, d))
                    changed = True
        closure.update(new_pairs)
    return closure


def get_activities(log: EventLog) -> Set[str]:
    """Get the set of activities appearing in the log (ΣL)."""
    activities = set()
    for trace in log:
        for event in trace:
            activities.add(event['concept:name'])
    return activities


def get_start_activities(log: EventLog) -> Set[str]:
    """Get the set of start activities in the log (L▷)."""
    start_activities = set()
    for trace in log:
        if len(trace) > 0:
            start_activities.add(trace[0]['concept:name'])
    return start_activities


def get_end_activities(log: EventLog) -> Set[str]:
    """Get the set of end activities in the log (L□)."""
    end_activities = set()
    for trace in log:
        if len(trace) > 0:
            end_activities.add(trace[-1]['concept:name'])
    return end_activities


def has_empty_trace(log: EventLog) -> bool:
    """Check if the log contains an empty trace (⟨⟩ ∈ L)."""
    for trace in log:
        if len(trace) == 0:
            return True
    return False


def mine_dg(log: EventLog) -> List[Set[str]]:
    """
    MineDG: Generate a candidate partition for a choice graph cut (Algorithm 1).

    This algorithm generates a partition of activities that ensures acyclicity
    by merging parts that contain mutually reachable activities.

    Args:
        log: Event log

    Returns:
        Partition of activities (list of sets). If single set, no valid cut exists.
    """
    activities = get_activities(log)
    dfg = compute_dfg_relation(log)
    dfg_tc = compute_transitive_closure(dfg)

    # Initialize: each activity in its own part
    parts = {activity: {activity} for activity in activities}

    # Merge parts for mutually reachable activities
    for a1 in activities:
        for a2 in activities:
            if (a1, a2) in dfg_tc and (a2, a1) in dfg_tc:
                # Merge the parts containing a1 and a2
                part_a1 = parts[a1]
                part_a2 = parts[a2]
                if part_a1 != part_a2:
                    merged = part_a1 | part_a2
                    for activity in merged:
                        parts[activity] = merged

    # Return unique parts
    unique_parts = list(set(frozenset(part) for part in parts.values()))
    return [set(part) for part in unique_parts]


def is_valid_choice_graph_cut(
    log: EventLog,
    parts: List[Set[str]],
    dfg: Optional[Set[Tuple[str, str]]] = None
) -> bool:
    """
    Check if a partition forms a valid choice graph cut (Definition 5).

    A choice graph cut (A, G) is valid if for all Ai, Aj:
    1. (Ai 7→Aj ∧ Ai ≠ Aj) ⇔ (Ai, Aj) ∈ E
    2. Ai ∩ L▷ ≠ ∅ ⇔ (▷, Ai) ∈ E
    3. Ai ∩ L□ ≠ ∅ ⇔ (Ai, □) ∈ E
    4. ⟨⟩ ∈ L ⇔ (▷, □) ∈ E
    5. (Ai 7→+ Aj ∧ Aj 7→+ Ai) ⇒ Ai = Aj

    Args:
        log: Event log
        parts: Partition of activities
        dfg: Optional pre-computed DFG relation

    Returns:
        True if the partition forms a valid choice graph cut
    """
    if dfg is None:
        dfg = compute_dfg_relation(log)

    dfg_tc = compute_transitive_closure(dfg)
    start_activities = get_start_activities(log)
    end_activities = get_end_activities(log)
    has_empty = has_empty_trace(log)

    # Condition 5: Acyclicity (mutually reachable → same part)
    for i, Ai in enumerate(parts):
        for j, Aj in enumerate(parts):
            if i != j:
                # Check if any activity in Ai is mutually reachable with any in Aj
                for a in Ai:
                    for b in Aj:
                        if (a, b) in dfg_tc and (b, a) in dfg_tc:
                            return False  # Violates acyclicity

    # Conditions 1-4 will be satisfied by the construction in create_choice_graph_from_cut
    # These conditions define a unique choice graph for a given valid partition
    return True


def create_choice_graph_from_cut(
    log: EventLog,
    parts: List[Set[str]],
    sub_models: Dict[int, POWL]
) -> DecisionGraph:
    """
    Create a choice graph from a valid cut (Definition 5).

    Given a valid partition, the requirements of Definition 5 uniquely
    define a choice graph. This method constructs that graph.

    Args:
        log: Event log
        parts: Partition of activities
        sub_models: Mapping from part index to POWL model

    Returns:
        DecisionGraph representing the choice graph
    """
    dfg = compute_dfg_relation(log)
    start_activities = get_start_activities(log)
    end_activities = get_end_activities(log)
    has_empty = has_empty_trace(log)

    # Create nodes from sub-models
    nodes = list(sub_models.values())
    order = BinaryRelation(nodes)

    # Build edges according to Definition 5
    for i, Ai in enumerate(parts):
        for j, Aj in enumerate(parts):
            if i == j:
                continue

            # Condition 1: (Ai 7→Aj ∧ Ai ≠ Aj) ⇔ (Ai, Aj) ∈ E
            has_dfg_edge = any((a, b) in dfg for a in Ai for b in Aj)
            if has_dfg_edge:
                order.add_edge(sub_models[i], sub_models[j])

    # Identify start and end nodes
    start_node_indices = []
    end_node_indices = []

    for i, Ai in enumerate(parts):
        # Condition 2: Ai ∩ L▷ ≠ ∅ ⇔ (▷, Ai) ∈ E
        if len(Ai & start_activities) > 0:
            start_node_indices.append(i)

        # Condition 3: Ai ∩ L□ ≠ ∅ ⇔ (Ai, □) ∈ E
        if len(Ai & end_activities) > 0:
            end_node_indices.append(i)

    # Condition 4: ⟨⟩ ∈ L ⇔ (▷, □) ∈ E
    empty_path = has_empty

    start_nodes = [sub_models[i] for i in start_node_indices]
    end_nodes = [sub_models[i] for i in end_node_indices]

    return DecisionGraph(order, start_nodes, end_nodes, empty_path)


def project_log(log: EventLog, activities: Set[str]) -> EventLog:
    """
    Project an event log onto a subset of activities (Definition 6).

    proj(L, A) = {σ↾A | σ ∈ L ∧ σ↾A ≠ ⟨⟩}

    Args:
        log: Event log
        activities: Subset of activities to project onto

    Returns:
        Projected event log
    """
    projected_traces = []

    for trace in log:
        # Filter events by activity and preserve order
        projected_events = [
            event for event in trace
            if event['concept:name'] in activities
        ]

        # Only include if non-empty
        if len(projected_events) > 0:
            # Create new trace with projected events
            from pm4py.objects.log.obj import Trace
            projected_traces.append(Trace(projected_events))

    # Create new event log
    from pm4py.objects.log.obj import EventLog
    return EventLog(projected_traces)


def language(powl_model: POWL) -> List[List[str]]:
    """
    Compute the language of a POWL model (Definition 3).

    L(a) = {⟨a⟩} for a ∈ Σ
    L(τ) = {⟨⟩}
    L(⟲(ψ1, ψ2)) = L(ψ1) · (L(ψ2) · L(ψ1))*
    L(≺(ψ1, ..., ψn)) = order-preserving shuffle
    L(G) = concatenation along all paths in G

    Note: This is a simplified implementation for basic models.
    For complex models, this may return an approximation.

    Args:
        powl_model: POWL model

    Returns:
        List of traces (each trace is a list of activity labels)
    """
    from pm4py.objects.powl.obj import SilentTransition, StrictPartialOrder, OperatorPOWL

    # Base case: Activity
    if isinstance(powl_model, Transition):
        if powl_model._label is None:
            return [[]]  # Silent transition = empty trace
        else:
            return [[powl_model._label]]

    # Base case: Silent transition
    if isinstance(powl_model, SilentTransition):
        return [[]]

    # Loop operator
    if isinstance(powl_model, OperatorPOWL) and powl_model.operator == Operator.LOOP:
        if len(powl_model.children) != 2:
            return []

        do_part = language(powl_model.children[0])
        redo_part = language(powl_model.children[1])

        # L(ψ1) · (L(ψ2) · L(ψ1))*
        # Simplified: just return do_part for now
        # Full implementation would handle the Kleene star
        return do_part

    # Partial order
    if isinstance(powl_model, StrictPartialOrder):
        # Simplified: return sequential order
        result = []
        for child in powl_model.children:
            result.extend(language(child))
        return [result] if result else [[]]

    # Decision graph / Choice graph
    if isinstance(powl_model, DecisionGraph):
        # L(G) = concatenation along all paths from start to end
        return _language_choice_graph(powl_model)

    # Default: empty language
    return [[]]


def _language_choice_graph(cg: DecisionGraph) -> List[List[str]]:
    """
    Compute the language of a choice graph by enumerating all paths.

    Args:
        cg: Choice graph

    Returns:
        List of traces
    """
    from pm4py.objects.powl.obj import StartNode, EndNode

    def find_all_paths(current_node, current_path, visited):
        """Recursively find all paths from current node to end."""
        if isinstance(current_node, EndNode):
            return [current_path]

        if current_node in visited:
            return []  # Avoid cycles

        visited.add(current_node)
        paths = []

        # Get successors
        if hasattr(current_node, 'label'):
            # It's a Transition/activity
            successors = cg.order.get_postset(current_node)
            new_path = current_path + [current_node.label] if current_node.label else current_path
        elif isinstance(current_node, StartNode):
            successors = cg.order.get_postset(current_node)
            new_path = current_path
        else:
            # POWL node
            successors = cg.order.get_postset(current_node)
            lang = language(current_node)
            if lang and lang[0]:
                new_path = current_path + lang[0]
            else:
                new_path = current_path

        for successor in successors:
            paths.extend(find_all_paths(successor, new_path, visited.copy()))

        return paths

    return find_all_paths(cg.start, [], set())


def validate_acyclicity(cg: DecisionGraph) -> bool:
    """
    Validate that a choice graph is acyclic (Definition 5, condition 5).

    (Ai 7→+ Aj ∧ Aj 7→+ Ai) ⇒ Ai = Aj

    In practice, this means no node should be reachable from itself
    through the choice graph (excluding the start/end sentinel cycle).

    Args:
        cg: Choice graph to validate

    Returns:
        True if the graph is acyclic
    """
    from pm4py.objects.powl.obj import StartNode, EndNode

    # Check each non-sentinel node for cycles
    for node in cg.children:
        visited = set()
        stack = [node]

        while stack:
            current = stack.pop()
            if current in visited:
                if current == node and current != cg.start and current != cg.end:
                    return False  # Found a cycle
                continue

            visited.add(current)
            successors = cg.order.get_postset(current)
            for successor in successors:
                if successor not in (cg.start, cg.end):
                    stack.append(successor)

    return True


__all__ = [
    "ChoiceGraphCut",
    "compute_dfg",
    "compute_dfg_relation",
    "compute_transitive_closure",
    "get_activities",
    "get_start_activities",
    "get_end_activities",
    "has_empty_trace",
    "mine_dg",
    "is_valid_choice_graph_cut",
    "create_choice_graph_from_cut",
    "project_log",
    "language",
    "validate_acyclicity",
]
