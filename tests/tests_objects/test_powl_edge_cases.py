"""
Edge Case Tests for POWL 2.0 Choice Graph Discovery

Tests boundary conditions and edge cases to ensure robustness.
"""

import pytest
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.powl.inductive.variants.im_choice_graph import (
    InductiveMinerChoiceGraphMaximal,
)
from pm4py.objects.powl.obj import DecisionGraph, Transition
from pm4py.objects.powl.BinaryRelation import BinaryRelation


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_log(self):
        """Test discovery with completely empty log."""
        log = EventLog([])  # No traces at all

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        # Empty log should return a silent transition or similar
        assert result is not None
        print("✓ Empty log handled correctly")

    def test_log_with_empty_traces(self):
        """Test discovery with traces that have no activities."""
        log = EventLog([
            Trace([]),  # Empty trace
            Trace([]),  # Another empty trace
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Log with empty traces handled correctly")

    def test_single_activity_log(self):
        """Test discovery with only one activity."""
        log = EventLog([
            Trace([Event({'concept:name': 'a'})]),
            Trace([Event({'concept:name': 'a'})]),
            Trace([Event({'concept:name': 'a'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        # Should discover a single activity
        if isinstance(result, Transition):
            assert result.label == 'a'
        print("✓ Single activity log handled correctly")

    def test_single_trace_log(self):
        """Test discovery with only one unique trace."""
        log = EventLog([
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Single trace log handled correctly")

    def test_all_traces_identical(self):
        """Test discovery where all traces are identical."""
        log = EventLog([
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ All identical traces handled correctly")

    def test_long_trace(self):
        """Test discovery with very long trace."""
        activities = [f"activity_{i}" for i in range(100)]
        log = EventLog([
            Trace([Event({'concept:name': act}) for act in activities])
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Long trace (100 activities) handled correctly")

    def test_no_choice_structure(self):
        """Test discovery with sequential process (no choices)."""
        log = EventLog([
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'}), Event({'concept:name': 'c'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Sequential process (no choices) handled correctly")

    def test_maximal_concurrency(self):
        """Test discovery with all activities concurrent."""
        log = EventLog([
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'}), Event({'concept:name': 'c'})]),
            Trace([Event({'concept:name': 'b'}), Event({'concept:name': 'a'}), Event({'concept:name': 'c'})]),
            Trace([Event({'concept:name': 'c'}), Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
            Trace([Event({'concept:name': 'c'}), Event({'concept:name': 'b'}), Event({'concept:name': 'a'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Maximal concurrency handled correctly")

    def test_self_loop(self):
        """Test discovery with activity that repeats immediately."""
        # This might represent a self-loop in the process
        log = EventLog([
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'a'}), Event({'concept:name': 'b'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Self-loop trace handled correctly")

    def test_sparse_choices(self):
        """Test discovery with many activities but few choices."""
        # Long sequential process with occasional choices
        log = EventLog([
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'}), Event({'concept:name': 'c'}),
                   Event({'concept:name': 'd'}), Event({'concept:name': 'e'})]),
            Trace([Event({'concept:name': 'a'}), Event({'concept:name': 'b'}), Event({'concept:name': 'x'}),
                   Event({'concept:name': 'd'}), Event({'concept:name': 'e'})]),
        ])

        miner = InductiveMinerChoiceGraphMaximal()
        result = miner.apply(log)

        assert result is not None
        print("✓ Sparse choices handled correctly")


class TestSoundnessEdgeCases:
    """Test soundness validation on edge cases."""

    def test_single_node_graph(self):
        """Test soundness of graph with only one node."""
        a = Transition('a')
        order = BinaryRelation([a])
        # No edges at all

        from pm4py.objects.powl.obj import StartNode, EndNode
        cg = DecisionGraph(order, [a], [a])

        report = cg.get_soundness_report()
        # Single node graph should be sound
        assert report['is_sound'], "Single node graph should be sound"
        print("✓ Single node graph validated as sound")

    def test_linear_chain(self):
        """Test soundness of a simple linear chain."""
        a = Transition('a')
        b = Transition('b')
        c = Transition('c')

        order = BinaryRelation([a, b, c])
        order.add_edge(a, b)
        order.add_edge(b, c)

        cg = DecisionGraph(order, [a], [c])

        report = cg.get_soundness_report()
        assert report['is_sound'], "Linear chain should be sound"
        print("✓ Linear chain validated as sound")

    def test_diamond_pattern(self):
        """Test soundness of diamond pattern (merge after split)."""
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

        report = cg.get_soundness_report()
        assert report['is_sound'], "Diamond pattern should be sound"
        print("✓ Diamond pattern validated as sound")


def run_edge_case_tests():
    """Run all edge case tests."""
    print("=" * 70)
    print("POWL 2.0 Edge Case Tests")
    print("=" * 70)

    test_classes = [
        TestEdgeCases(),
        TestSoundnessEdgeCases(),
    ]

    for test_class in test_classes:
        print(f"\n{test_class.__name__}:")
        for method_name in dir(test_class):
            if method_name.startswith('test_'):
                method = getattr(test_class, method_name)
                try:
                    method()
                except Exception as e:
                    print(f"  ✗ {method_name}: {e}")

    print("\n" + "=" * 70)
    print("All edge case tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    run_edge_case_tests()
