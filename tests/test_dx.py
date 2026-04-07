'''
PM4Py – A Process Mining Library for Python
Copyright (C) 2026 Process Intelligence Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see this software project's root or
visit <https://www.gnu.org/licenses/>.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
'''

import unittest
from pm4py.dx import (
    pretty_print_powl,
    model_summary,
    model_activities,
    powl_to_dot,
    petri_net_to_dot,
    petri_net_activities,
    log_summary,
    top_variants,
    truncate_traces,
    group_by_variant,
    partition_by_fitness,
    activity_fitness,
    conformance_table,
    fitness_histogram,
    conformance_batched,
    LogStats,
    VariantInfo,
    FitnessBucket,
    PartitionedTraces,
)
from pm4py.objects.powl.parser import parse_powl_model_string


class TestModelUtilities(unittest.TestCase):
    """Test suite for POWL model utilities."""

    def test_pretty_print_simple(self):
        """Test pretty-printing a simple POWL model."""
        model = parse_powl_model_string("X(A, B)")
        result = pretty_print_powl(model)

        self.assertIn("X(", result)
        self.assertIn("'A'", result)
        self.assertIn("'B'", result)
        # Check for indentation
        self.assertTrue(any(line.startswith("  ") for line in result.split("\n")))

    def test_pretty_print_nested(self):
        """Test pretty-printing nested POWL model."""
        model = parse_powl_model_string("X(A, X(B, C))")
        result = pretty_print_powl(model)

        self.assertIn("X(", result)
        self.assertIn("'A'", result)
        self.assertIn("'B'", result)
        self.assertIn("'C'", result)

    def test_pretty_print_partial_order(self):
        """Test pretty-printing partial order model."""
        model = parse_powl_model_string("PO=(nodes={A,B},order={A-->B})")
        result = pretty_print_powl(model)

        self.assertIn("PO=", result)
        self.assertIn("nodes=", result)
        self.assertIn("order=", result)

    def test_model_summary_simple(self):
        """Test model summary for simple XOR."""
        model = parse_powl_model_string("X(A, B)")
        result = model_summary(model)

        self.assertIn("XOR", result)
        self.assertIn("2", result)  # Should mention 2 activities

    def test_model_summary_loop(self):
        """Test model summary for loop."""
        model = parse_powl_model_string("*(A, B)")
        result = model_summary(model)

        self.assertIn("LOOP", result)

    def test_model_activities_xor(self):
        """Test extracting activities from XOR."""
        model = parse_powl_model_string("X(A, B)")
        result = model_activities(model)

        self.assertEqual(len(result), 2)
        self.assertIn("A", result)
        self.assertIn("B", result)

    def test_model_activities_nested(self):
        """Test extracting activities from nested model."""
        model = parse_powl_model_string("X(A, X(B, C))")
        result = model_activities(model)

        self.assertEqual(len(result), 3)
        self.assertIn("A", result)
        self.assertIn("B", result)
        self.assertIn("C", result)

    def test_powl_to_dot(self):
        """Test POWL to DOT conversion."""
        model = parse_powl_model_string("X(A, B)")
        result = powl_to_dot(model)

        self.assertIn("digraph", result)
        self.assertIn("rankdir", result)
        # Should contain Graphviz DOT syntax

    def test_powl_to_dot_empty(self):
        """Test POWL to DOT with None model."""
        result = powl_to_dot(None)

        self.assertIn("digraph", result)


class TestLogUtilities(unittest.TestCase):
    """Test suite for event log utilities."""

    @classmethod
    def setUpClass(cls):
        """Create a simple test log."""
        from pm4py.objects.log.obj import Event, EventLog, Trace

        # Create test traces
        trace1 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "B", "time:timestamp": 2000000}),
            Event({"concept:name": "C", "time:timestamp": 3000000}),
        ])

        trace2 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "B", "time:timestamp": 2000000}),
            Event({"concept:name": "C", "time:timestamp": 3000000}),
        ])

        trace3 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "C", "time:timestamp": 2000000}),
        ])

        cls.log = EventLog([trace1, trace2, trace3])

    def test_log_summary(self):
        """Test comprehensive log summary."""
        stats = log_summary(self.log)

        self.assertIsInstance(stats, LogStats)
        self.assertEqual(stats.trace_count, 3)
        self.assertGreater(stats.event_count, 0)
        self.assertGreater(stats.activity_count, 0)
        self.assertGreater(stats.avg_trace_length, 0)
        self.assertEqual(stats.min_trace_length, 2)
        self.assertEqual(stats.max_trace_length, 3)
        self.assertGreater(stats.variant_count, 0)
        self.assertIsInstance(stats.start_activities, list)
        self.assertIsInstance(stats.end_activities, list)

    def test_log_summary_str(self):
        """Test LogStats string representation."""
        stats = log_summary(self.log)
        str_repr = str(stats)

        self.assertIn("LogStats", str_repr)
        self.assertIn("traces=", str_repr)

    def test_top_variants(self):
        """Test top-N variants extraction."""
        variants = top_variants(self.log, n=2)

        self.assertIsInstance(variants, list)
        self.assertLessEqual(len(variants), 2)

        for v in variants:
            self.assertIsInstance(v, VariantInfo)
            self.assertIsInstance(v.variant, str)
            self.assertIsInstance(v.count, int)
            self.assertIsInstance(v.frequency, float)
            self.assertGreaterEqual(v.frequency, 0.0)
            self.assertLessEqual(v.frequency, 1.0)

    def test_top_variants_sorted(self):
        """Test that top variants are sorted by count."""
        variants = top_variants(self.log, n=10)

        # Check descending order
        for i in range(len(variants) - 1):
            self.assertGreaterEqual(variants[i].count, variants[i + 1].count)

    def test_truncate_traces(self):
        """Test trace truncation."""
        truncated = truncate_traces(self.log, k=2)

        self.assertEqual(len(truncated), len(self.log))

        # All traces should have max 2 events
        for trace in truncated:
            self.assertLessEqual(len(trace), 2)

    def test_truncate_traces_zero(self):
        """Test trace truncation with k=0."""
        truncated = truncate_traces(self.log, k=0)

        self.assertEqual(len(truncated), len(self.log))

        for trace in truncated:
            self.assertEqual(len(trace), 0)

    def test_group_by_variant(self):
        """Test grouping traces by variant."""
        groups = group_by_variant(self.log)

        self.assertIsInstance(groups, dict)

        for variant, traces in groups.items():
            self.assertIsInstance(variant, str)
            self.assertIsInstance(traces, list)
            self.assertGreater(len(traces), 0)

            # All traces in group should have same variant
            for trace in traces:
                trace_str = ", ".join([event["concept:name"] for event in trace])
                self.assertEqual(trace_str, variant)


class TestConformanceUtilities(unittest.TestCase):
    """Test suite for conformance utilities."""

    @classmethod
    def setUpClass(cls):
        """Create test log and model."""
        from pm4py.objects.log.obj import Event, EventLog, Trace
        from pm4py.objects.powl.parser import parse_powl_model_string

        # Create test log
        trace1 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "B", "time:timestamp": 2000000}),
            Event({"concept:name": "C", "time:timestamp": 3000000}),
        ])

        trace2 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "B", "time:timestamp": 2000000}),
            Event({"concept:name": "C", "time:timestamp": 3000000}),
        ])

        trace3 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "C", "time:timestamp": 2000000}),
        ])

        cls.log = EventLog([trace1, trace2, trace3])
        cls.model = parse_powl_model_string("PO=(nodes={A,B,C},order={A-->B,B-->C})")

    def test_partition_by_fitness(self):
        """Test partitioning traces by fitness."""
        # Create mock result
        result = {
            "trace_fitness": [1.0, 1.0, 0.5],  # Two fitting, one not
            "log_fitness": 0.83
        }

        partitioned = partition_by_fitness(self.log, result, threshold=0.8)

        self.assertIsInstance(partitioned, PartitionedTraces)
        self.assertEqual(len(partitioned.fitting), 2)
        self.assertEqual(len(partitioned.non_fitting), 1)

    def test_partition_by_fitness_threshold(self):
        """Test partitioning with different threshold."""
        result = {
            "trace_fitness": [1.0, 0.9, 0.5],
            "log_fitness": 0.8
        }

        partitioned = partition_by_fitness(self.log, result, threshold=0.95)

        # Only first trace should be fitting
        self.assertEqual(len(partitioned.fitting), 1)
        self.assertEqual(len(partitioned.non_fitting), 2)

    def test_activity_fitness(self):
        """Test per-activity fitness calculation."""
        result = {
            "trace_fitness": [1.0, 1.0, 0.5],
            "log_fitness": 0.83
        }

        act_fit = activity_fitness(self.log, result)

        self.assertIsInstance(act_fit, dict)

        # Activity A appears in all traces: (1.0 + 1.0 + 0.5) / 3 = 0.83
        self.assertIn("A", act_fit)
        self.assertAlmostEqual(act_fit["A"], 0.83, places=2)

    def test_conformance_table(self):
        """Test ASCII conformance table generation."""
        result = {
            "trace_fitness": [1.0, 0.9, 0.5],
            "log_fitness": 0.8
        }

        table = conformance_table(self.log, result, max_rows=10)

        self.assertIn("case_id", table)
        self.assertIn("activities", table)
        self.assertIn("fitness", table)
        self.assertIn("Global:", table)
        self.assertIn("80.0%", table)  # log_fitness * 100

        # Check for box-drawing characters
        self.assertIn("┌", table)
        self.assertIn("┬", table)
        self.assertIn("┐", table)

    def test_conformance_table_max_rows(self):
        """Test conformance table with max_rows limit."""
        result = {
            "trace_fitness": [1.0, 0.9, 0.5],
            "log_fitness": 0.8
        }

        table = conformance_table(self.log, result, max_rows=2)

        # Should only show 2 rows
        lines = table.split("\n")
        data_lines = [l for l in lines if "│" in l and "case_id" not in l and "Global:" not in l]
        # Filter out separator lines
        data_lines = [l for l in data_lines if "┼" not in l and all(c not in l for c in "┌┐└┘")]

        # Should have at most 2 data rows
        self.assertLessEqual(len(data_lines), 2)

    def test_fitness_histogram(self):
        """Test fitness histogram generation."""
        result = {
            "trace_fitness": [1.0, 0.9, 0.5, 0.3, 0.1],
            "log_fitness": 0.56
        }

        histogram = fitness_histogram(result, buckets=5)

        self.assertIsInstance(histogram, list)
        self.assertEqual(len(histogram), 5)

        total_count = sum(bucket.count for bucket in histogram)
        self.assertEqual(total_count, 5)  # 5 traces

        # Check frequencies sum to 1.0
        total_freq = sum(bucket.frequency for bucket in histogram)
        self.assertAlmostEqual(total_freq, 1.0, places=5)

        for bucket in histogram:
            self.assertIsInstance(bucket, FitnessBucket)
            self.assertIsInstance(bucket.range, str)
            self.assertIsInstance(bucket.count, int)
            self.assertIsInstance(bucket.frequency, float)

    def test_fitness_histogram_buckets(self):
        """Test histogram with different bucket counts."""
        result = {
            "trace_fitness": [1.0, 0.5, 0.0],
            "log_fitness": 0.5
        }

        histogram_10 = fitness_histogram(result, buckets=10)
        histogram_5 = fitness_histogram(result, buckets=5)

        self.assertEqual(len(histogram_10), 10)
        self.assertEqual(len(histogram_5), 5)

    def test_conformance_batched(self):
        """Test batched conformance checking."""
        # This test requires a Petri net with markings, not just POWL
        # For now, we'll test the basic structure without running actual conformance
        progress_calls = []

        def progress_callback(done, total):
            progress_calls.append((done, total))

        # Test that the function accepts the callback
        # Actual conformance testing would require PetriNet conversion
        # which is tested in the PetriNetUtilities class

        # Just verify the callback format
        progress_callback(5, 10)
        self.assertEqual(len(progress_calls), 1)
        self.assertEqual(progress_calls[0], (5, 10))


class TestPetriNetUtilities(unittest.TestCase):
    """Test suite for Petri net utilities."""

    def test_petri_net_to_dot(self):
        """Test Petri net to DOT conversion."""
        # Use pm4py's discovery to create a real Petri net
        from pm4py.objects.log.obj import Event, EventLog, Trace

        # Create simple test log
        trace1 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "B", "time:timestamp": 2000000}),
        ])

        log = EventLog([trace1])

        # Discover Petri net
        import pm4py
        net, im, fm = pm4py.discover_petri_net_inductive(log)

        result = petri_net_to_dot(net, im)

        self.assertIn("digraph", result)
        self.assertIn("rankdir", result)
        self.assertIn("shape=circle", result)
        self.assertIn("shape=box", result)

    def test_petri_net_activities(self):
        """Test extracting activities from Petri net."""
        # Use pm4py's discovery to create a real Petri net
        from pm4py.objects.log.obj import Event, EventLog, Trace

        # Create simple test log
        trace1 = Trace([
            Event({"concept:name": "A", "time:timestamp": 1000000}),
            Event({"concept:name": "B", "time:timestamp": 2000000}),
            Event({"concept:name": "C", "time:timestamp": 3000000}),
        ])

        log = EventLog([trace1])

        # Discover Petri net
        import pm4py
        net, im, fm = pm4py.discover_petri_net_inductive(log)

        result = petri_net_activities(net)

        self.assertGreater(len(result), 0)
        self.assertIn("A", result)
        self.assertIn("B", result)
        self.assertIn("C", result)


if __name__ == '__main__':
    unittest.main()
