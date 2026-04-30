"""
T004 — POWL footprints SEQUENCE + PARALLEL operators
Tests for get_footprints_of_sequence and get_footprints_of_parallel
in pm4py.algo.discovery.footprints.powl.variants.bottomup
"""
import pytest
from pm4py.objects.powl.obj import Transition, SilentTransition, OperatorPOWL, StrictPartialOrder
from pm4py.objects.process_tree.obj import Operator
from pm4py.algo.discovery.footprints.powl.variants.bottomup import (
    get_footprints_powl,
    apply,
    SEQUENCE,
    PARALLEL,
    START_ACTIVITIES,
    END_ACTIVITIES,
    ACTIVITIES,
    SKIPPABLE,
    ACTIVITIES_ALWAYS_HAPPENING,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_seq(*labels):
    """Build OperatorPOWL SEQUENCE over labeled Transitions."""
    children = [Transition(label=lbl) for lbl in labels]
    return OperatorPOWL(operator=Operator.SEQUENCE, children=children)


def make_par(*labels):
    """Build OperatorPOWL PARALLEL over labeled Transitions."""
    children = [Transition(label=lbl) for lbl in labels]
    return OperatorPOWL(operator=Operator.PARALLEL, children=children)


def fp(node):
    return get_footprints_powl(node, {})


# ---------------------------------------------------------------------------
# SEQUENCE tests
# ---------------------------------------------------------------------------

class TestSequenceOperator:

    def test_sequence_two_children_start_activities(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert result[START_ACTIVITIES] == {"A"}

    def test_sequence_two_children_end_activities(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert result[END_ACTIVITIES] == {"B"}

    def test_sequence_two_children_activities(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert result[ACTIVITIES] == {"A", "B"}

    def test_sequence_two_children_sequence_edge(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert ("A", "B") in result[SEQUENCE]

    def test_sequence_two_children_no_parallel(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert result[PARALLEL] == set()

    def test_sequence_two_children_not_skippable(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert result[SKIPPABLE] is False

    def test_sequence_three_children_start_end(self):
        node = make_seq("A", "B", "C")
        result = fp(node)
        assert result[START_ACTIVITIES] == {"A"}
        assert result[END_ACTIVITIES] == {"C"}

    def test_sequence_three_children_sequence_edges(self):
        node = make_seq("A", "B", "C")
        result = fp(node)
        assert ("A", "B") in result[SEQUENCE]
        assert ("B", "C") in result[SEQUENCE]

    def test_sequence_three_children_activities(self):
        node = make_seq("A", "B", "C")
        result = fp(node)
        assert result[ACTIVITIES] == {"A", "B", "C"}

    def test_sequence_with_silent_transition_skippable_middle(self):
        """Sequence [A, tau, B]: tau is skippable, so A->B skip edge should appear."""
        A = Transition(label="A")
        tau = SilentTransition()
        B = Transition(label="B")
        node = OperatorPOWL(operator=Operator.SEQUENCE, children=[A, tau, B])
        result = get_footprints_powl(node, {})
        # A->B because tau in the middle is skippable
        assert ("A", "B") in result[SEQUENCE]

    def test_sequence_activities_always_happening(self):
        node = make_seq("A", "B")
        result = fp(node)
        assert result[ACTIVITIES_ALWAYS_HAPPENING] == {"A", "B"}

    def test_sequence_apply_entry_point(self):
        """apply() (public entry point) works for SEQUENCE nodes."""
        node = make_seq("X", "Y")
        result = apply(node)
        assert result[START_ACTIVITIES] == {"X"}
        assert result[END_ACTIVITIES] == {"Y"}
        assert ("X", "Y") in result[SEQUENCE]


# ---------------------------------------------------------------------------
# PARALLEL tests
# ---------------------------------------------------------------------------

class TestParallelOperator:

    def test_parallel_two_children_start_activities(self):
        node = make_par("A", "B")
        result = fp(node)
        assert result[START_ACTIVITIES] == {"A", "B"}

    def test_parallel_two_children_end_activities(self):
        node = make_par("A", "B")
        result = fp(node)
        assert result[END_ACTIVITIES] == {"A", "B"}

    def test_parallel_two_children_activities(self):
        node = make_par("A", "B")
        result = fp(node)
        assert result[ACTIVITIES] == {"A", "B"}

    def test_parallel_two_children_concurrent_pairs(self):
        node = make_par("A", "B")
        result = fp(node)
        assert ("A", "B") in result[PARALLEL]
        assert ("B", "A") in result[PARALLEL]

    def test_parallel_two_children_no_sequence(self):
        node = make_par("A", "B")
        result = fp(node)
        assert result[SEQUENCE] == set()

    def test_parallel_two_children_not_skippable(self):
        node = make_par("A", "B")
        result = fp(node)
        assert result[SKIPPABLE] is False

    def test_parallel_three_children_all_concurrent(self):
        node = make_par("A", "B", "C")
        result = fp(node)
        pairs = result[PARALLEL]
        assert ("A", "B") in pairs
        assert ("B", "A") in pairs
        assert ("A", "C") in pairs
        assert ("C", "A") in pairs
        assert ("B", "C") in pairs
        assert ("C", "B") in pairs

    def test_parallel_activities_always_happening(self):
        node = make_par("A", "B")
        result = fp(node)
        assert result[ACTIVITIES_ALWAYS_HAPPENING] == {"A", "B"}

    def test_parallel_apply_entry_point(self):
        """apply() (public entry point) works for PARALLEL nodes."""
        node = make_par("X", "Y")
        result = apply(node)
        assert result[START_ACTIVITIES] == {"X", "Y"}
        assert ("X", "Y") in result[PARALLEL]
        assert ("Y", "X") in result[PARALLEL]

    def test_parallel_skippable_all_silent(self):
        """Parallel of two SilentTransitions is skippable."""
        t1 = SilentTransition()
        t2 = SilentTransition()
        node = OperatorPOWL(operator=Operator.PARALLEL, children=[t1, t2])
        result = get_footprints_powl(node, {})
        assert result[SKIPPABLE] is True
        assert result[ACTIVITIES] == set()


# ---------------------------------------------------------------------------
# T005 — Alignment DP SEQUENCE + PARALLEL (already implemented, verify here)
# ---------------------------------------------------------------------------

class TestAlignmentDPSequenceParallel:
    """Smoke-tests confirming SEQUENCE and PARALLEL already work in dynamic_programming.py."""

    def _align(self, trace, tree):
        from pm4py.algo.conformance.alignments.process_tree.variants.dynamic_programming import (
            align_trace_with_process_tree,
        )
        return align_trace_with_process_tree(tuple(trace), tree)

    def _seq_tree(self, *labels):
        from pm4py.objects.process_tree.obj import ProcessTree, Operator as PTOp
        leaves = [ProcessTree(label=lbl) for lbl in labels]
        root = ProcessTree(operator=PTOp.SEQUENCE, children=leaves)
        for leaf in leaves:
            leaf.parent = root
        return root

    def _par_tree(self, *labels):
        from pm4py.objects.process_tree.obj import ProcessTree, Operator as PTOp
        leaves = [ProcessTree(label=lbl) for lbl in labels]
        root = ProcessTree(operator=PTOp.PARALLEL, children=leaves)
        for leaf in leaves:
            leaf.parent = root
        return root

    def test_sequence_conforming_cost_zero(self):
        tree = self._seq_tree("A", "B")
        cost, alignment = self._align(["A", "B"], tree)
        assert cost == 0
        assert ("A", "A") in alignment
        assert ("B", "B") in alignment

    def test_sequence_non_conforming_cost_positive(self):
        tree = self._seq_tree("A", "B")
        cost, alignment = self._align(["B", "A"], tree)
        assert cost > 0

    def test_parallel_both_orderings_cost_zero(self):
        tree = self._par_tree("A", "B")
        cost_ab, _ = self._align(["A", "B"], tree)
        cost_ba, _ = self._align(["B", "A"], tree)
        assert cost_ab == 0
        assert cost_ba == 0
