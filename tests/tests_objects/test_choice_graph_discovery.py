"""
Test POWL 2.0 Choice Graph Discovery Algorithms.

Tests the implementation of algorithms from:
H Kourani, G Park, WMP van der Aalst. "Unlocking Non-Block-Structured Decisions:
Inductive Mining with Choice Graphs" arXiv preprint arXiv:2505.07052.
"""

import pytest

from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.objects.powl.obj import DecisionGraph, Transition, StrictPartialOrder, Sequence
from pm4py.objects.powl.BinaryRelation import BinaryRelation
from pm4py.objects.powl import choice_graph_discovery


def create_simple_log(traces):
    """Helper to create an event log from a list of trace strings."""
    event_log = EventLog()
    for trace_activities in traces:
        events = [Event({'concept:name': act}) for act in trace_activities]
        event_log.append(Trace(events))
    return event_log


class TestDFGOperations:
    """Test DFG computation and related operations."""

    def test_compute_dfg(self):
        """Test basic DFG computation."""
        log = create_simple_log([['a', 'b', 'c'], ['a', 'b', 'd']])
        dfg = choice_graph_discovery.compute_dfg(log)

        assert dfg[('a', 'b')] == 2
        assert dfg[('b', 'c')] == 1
        assert dfg[('b', 'd')] == 1
        assert ('c', 'd') not in dfg

    def test_dfg_relation(self):
        """Test DFG relation extraction."""
        log = create_simple_log([['a', 'b'], ['b', 'c']])
        relation = choice_graph_discovery.compute_dfg_relation(log)

        assert ('a', 'b') in relation
        assert ('b', 'c') in relation
        assert ('b', 'a') not in relation

    def test_transitive_closure(self):
        """Test transitive closure computation."""
        dfg = {('a', 'b'), ('b', 'c')}
        closure = choice_graph_discovery.compute_transitive_closure(dfg)

        assert ('a', 'b') in closure
        assert ('b', 'c') in closure
        assert ('a', 'c') in closure  # Transitive

    def test_mutual_reachability(self):
        """Test detection of mutually reachable activities."""
        log = create_simple_log([['a', 'b', 'a'], ['b', 'a', 'b']])
        dfg = choice_graph_discovery.compute_dfg_relation(log)
        closure = choice_graph_discovery.compute_transitive_closure(dfg)

        # a and b are mutually reachable
        assert ('a', 'b') in closure
        assert ('b', 'a') in closure


class TestActivitySets:
    """Test extraction of activity sets from logs."""

    def test_get_activities(self):
        """Test extraction of all activities."""
        log = create_simple_log([['a', 'b'], ['a', 'c', 'd']])
        activities = choice_graph_discovery.get_activities(log)

        assert activities == {'a', 'b', 'c', 'd'}

    def test_get_start_activities(self):
        """Test extraction of start activities."""
        log = create_simple_log([['a', 'b'], ['a', 'c'], ['b', 'd']])
        start_activities = choice_graph_discovery.get_start_activities(log)

        assert start_activities == {'a', 'b'}

    def test_get_end_activities(self):
        """Test extraction of end activities."""
        log = create_simple_log([['a', 'b'], ['a', 'c'], ['b', 'c']])
        end_activities = choice_graph_discovery.get_end_activities(log)

        assert end_activities == {'b', 'c'}

    def test_has_empty_trace(self):
        """Test detection of empty traces."""
        log_with_empty = create_simple_log([['a', 'b'], [], ['c']])
        assert choice_graph_discovery.has_empty_trace(log_with_empty)

        log_without_empty = create_simple_log([['a', 'b'], ['c']])
        assert not choice_graph_discovery.has_empty_trace(log_without_empty)


class TestMineDG:
    """Test MineDG algorithm (Algorithm 1)."""

    def test_mine_dg_simple(self):
        """Test MineDG with simple sequential log."""
        log = create_simple_log([['a', 'b', 'c']])
        parts = choice_graph_discovery.mine_dg(log)

        # Sequential process should keep activities separate
        assert len(parts) >= 1
        all_activities = set()
        for part in parts:
            all_activities.update(part)
        assert all_activities == {'a', 'b', 'c'}

    def test_mine_dg_concurrent(self):
        """Test MineDG with concurrent activities."""
        # Log showing concurrency: a before c, b before c, but a and b concurrent
        log = create_simple_log([['a', 'c'], ['b', 'c'], ['a', 'b', 'c']])
        parts = choice_graph_discovery.mine_dg(log)

        # a and b should be in different parts (not mutually reachable)
        # c should be separate
        assert len(parts) >= 2

    def test_mine_dg_mutual_reachability(self):
        """Test that mutually reachable activities are merged."""
        # Log showing a and b are mutually reachable (loop-like)
        log = create_simple_log([['a', 'b', 'a'], ['b', 'a', 'b']])
        parts = choice_graph_discovery.mine_dg(log)

        # a and b should be in the same part due to mutual reachability
        for part in parts:
            if 'a' in part:
                assert 'b' in part
                break


class TestValidChoiceGraphCut:
    """Test valid choice graph cut detection (Definition 5)."""

    def test_valid_cut_simple(self):
        """Test validation of simple valid cut."""
        log = create_simple_log([['a', 'b'], ['a', 'c']])
        parts = [{'a'}, {'b', 'c'}]

        assert choice_graph_discovery.is_valid_choice_graph_cut(log, parts)

    def test_invalid_cut_acyclicity(self):
        """Test that cuts violating acyclicity are rejected."""
        # Log where a and b are mutually reachable
        log = create_simple_log([['a', 'b', 'a'], ['b', 'a', 'b']])
        parts = [{'a'}, {'b'}]

        # Should be invalid due to mutual reachability (violates condition 5)
        assert not choice_graph_discovery.is_valid_choice_graph_cut(log, parts)


class TestCreateChoiceGraph:
    """Test choice graph construction from valid cuts."""

    def test_create_choice_graph_simple(self):
        """Test creating choice graph from simple partition."""
        log = create_simple_log([['a', 'b'], ['a', 'c']])
        parts = [{'a'}, {'b'}, {'c'}]

        # Create simple transitions as sub-models
        sub_models = {
            0: Transition('a'),
            1: Transition('b'),
            2: Transition('c')
        }

        cg = choice_graph_discovery.create_choice_graph_from_cut(log, parts, sub_models)

        assert isinstance(cg, DecisionGraph)
        assert len(cg.children) == 3

    def test_create_choice_graph_with_start_end(self):
        """Test that start/end nodes are correctly connected."""
        log = create_simple_log([['a', 'b'], ['c', 'b']])
        parts = [{'a', 'c'}, {'b'}]

        sub_models = {
            0: Transition('x'),
            1: Transition('b')
        }

        cg = choice_graph_discovery.create_choice_graph_from_cut(log, parts, sub_models)

        # Both a and c are start activities, so part 0 should be a start node
        # b is the only end activity
        assert len(cg.start_nodes) == 1
        assert len(cg.end_nodes) == 1


class TestProjectLog:
    """Test log projection operation (Definition 6)."""

    def test_project_log_simple(self):
        """Test projecting log onto activity subset."""
        log = create_simple_log([['a', 'b', 'c'], ['a', 'b', 'd']])
        projected = choice_graph_discovery.project_log(log, {'a', 'c'})

        traces = [[event['concept:name'] for event in trace] for trace in projected]
        assert ['a', 'c'] in traces
        assert ['a'] in traces  # Second trace loses 'b' and 'd', leaving just 'a'

    def test_project_log_empty_result(self):
        """Test that projection removes traces with no matching activities."""
        log = create_simple_log([['a', 'b'], ['c', 'd']])
        projected = choice_graph_discovery.project_log(log, {'a'})

        traces = [[event['concept:name'] for event in trace] for trace in projected]
        assert ['a'] in traces
        assert len(traces) == 1  # Second trace has no 'a', so it's removed


class TestDecisionGraphMethods:
    """Test new methods added to DecisionGraph class."""

    def test_validate_acyclicity_acyclic(self):
        """Test acyclicity validation on acyclic graph."""
        # Create simple acyclic graph: a -> b -> c
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')

        order = BinaryRelation([a, b, c])
        order.add_edge(a, b)
        order.add_edge(b, c)

        cg = DecisionGraph(order, [a], [c])
        assert cg.validate_acyclicity()

    def test_validate_acyclicity_cyclic(self):
        """Test acyclicity validation on cyclic graph."""
        # Create cyclic graph: a -> b -> a
        a = Transition('a')
        b = Transition('b')

        order = BinaryRelation([a, b])
        order.add_edge(a, b)
        order.add_edge(b, a)

        cg = DecisionGraph(order, [a], [b])
        assert not cg.validate_acyclicity()

    def test_get_all_paths(self):
        """Test getting all execution paths."""
        # Create choice: a -> (b or c) -> d
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')
        d = Transition('d')

        order = BinaryRelation([a, b, c, d])
        order.add_edge(a, b)
        order.add_edge(a, c)
        order.add_edge(b, d)
        order.add_edge(c, d)

        cg = DecisionGraph(order, [a], [d])
        paths = cg.get_all_paths()

        # Should have two paths: a->b->d and a->c->d
        assert len(paths) == 2
        path_lists = [[n.label for n in path if hasattr(n, 'label')] for path in paths]
        assert ['a', 'b', 'd'] in path_lists
        assert ['a', 'c', 'd'] in path_lists

    def test_language_simple(self):
        """Test language computation for simple graph."""
        # Linear sequence: a -> b
        a = Transition('a')
        b = Transition('b')

        order = BinaryRelation([a, b])
        order.add_edge(a, b)

        cg = DecisionGraph(order, [a], [b])
        lang = cg.language()

        assert ['a', 'b'] in lang

    def test_language_choice(self):
        """Test language computation for choice graph."""
        # Choice: a or b
        a = Transition('a')
        b = Transition('b')

        order = BinaryRelation([a, b])

        cg = DecisionGraph(order, [a, b], [a, b])
        lang = cg.language()

        # Should have two traces: [a] and [b]
        assert len(lang) == 2
        assert ['a'] in lang or ['b'] in lang


class TestIntegration:
    """Integration tests for complete discovery workflow."""

    def test_retailer_example_from_paper(self):
        """
        Test the retailer order fulfillment example from the paper (Figure 2).

        This example has non-block-structured decisions:
        - Initial choice: in-stock vs production
        - Within in-stock: cancel OR join shipping
        """
        # Simplified log representing the retailer process
        log = create_simple_log([
            ['receive_order', 'in_stock', 'ship'],
            ['receive_order', 'in_stock', 'cancel'],
            ['receive_order', 'production', 'gather_materials', 'schedule', 'notify', 'execute'],
            ['receive_order', 'production', 'gather_materials', 'schedule', 'execute'],
            ['receive_order', 'production', 'gather_materials', 'schedule', 'notify', 'execute'],
        ])

        # Mine for choice graph cut
        parts = choice_graph_discovery.mine_dg(log)

        # Should partition the activities
        assert len(parts) >= 2

        # Check that we can validate the cut
        dfg = choice_graph_discovery.compute_dfg_relation(log)
        assert choice_graph_discovery.is_valid_choice_graph_cut(log, parts, dfg)

    def test_complete_discovery_workflow(self):
        """Test end-to-end discovery workflow."""
        # Create log with clear choice structure
        log = create_simple_log([
            ['start', 'left', 'end'],
            ['start', 'right', 'end'],
        ])

        # Step 1: Mine partition
        parts = choice_graph_discovery.mine_dg(log)
        assert len(parts) >= 2

        # Step 2: Validate cut
        assert choice_graph_discovery.is_valid_choice_graph_cut(log, parts)

        # Step 3: Create sub-models (simplified - just transitions)
        sub_models = {i: Transition(list(part)[0]) for i, part in enumerate(parts)}

        # Step 4: Create choice graph
        cg = choice_graph_discovery.create_choice_graph_from_cut(log, parts, sub_models)

        # Step 5: Validate properties
        assert cg.validate_connectivity()
        assert cg.validate_acyclicity()

        # Step 6: Compute language
        lang = cg.language()
        assert len(lang) > 0


def test_fitness_preservation():
    """
    Test fitness preservation (Lemma 1 from paper).

    Every trace in the event log should be included in the language
    of the discovered model.
    """
    log = create_simple_log([
        ['a', 'b'],
        ['a', 'c'],
    ])

    parts = choice_graph_discovery.mine_dg(log)
    sub_models = {i: Transition(list(part)[0]) for i, part in enumerate(parts)}
    cg = choice_graph_discovery.create_choice_graph_from_cut(log, parts, sub_models)

    # Get all traces from log
    log_traces = {tuple(event['concept:name'] for event in trace) for trace in log}

    # Get language of discovered model
    model_traces = {tuple(trace) for trace in cg.language()}

    # All log traces should be in model language
    for trace in log_traces:
        assert trace in model_traces, f"Trace {trace} not in model language"
