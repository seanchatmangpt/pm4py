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



import unittest
from pm4py.analysis import calculate_complexity_metrics, compare_complexity
from pm4py.objects.powl.parser import parse_powl_model_string


class TestComplexityMetrics(unittest.TestCase):
    """Test suite for complexity metrics calculation."""

    def test_simple_activity(self):
        """Test complexity of a single activity."""
        model = parse_powl_model_string("A")
        metrics = calculate_complexity_metrics(model)

        self.assertEqual(metrics.node_count, 1)
        self.assertEqual(metrics.activity_count, 1)
        self.assertEqual(metrics.operator_count, 0)
        self.assertEqual(metrics.cyclomatic_complexity, 1.0)
        self.assertEqual(metrics.decision_points, 0)
        self.assertEqual(metrics.nesting_depth, 0)
        self.assertEqual(metrics.is_block_structured, True)

    def test_xor_choice(self):
        """Test complexity of XOR choice."""
        model = parse_powl_model_string("X(A, B)")
        metrics = calculate_complexity_metrics(model)

        self.assertEqual(metrics.xor_count, 1)
        self.assertEqual(metrics.cyclomatic_complexity, 2.0)  # 1 decision + 1
        self.assertEqual(metrics.decision_points, 1)
        self.assertGreater(metrics.control_flow_complexity, 0)

    def test_loop(self):
        """Test complexity of loop."""
        model = parse_powl_model_string("*(A, B)")
        metrics = calculate_complexity_metrics(model)

        self.assertEqual(metrics.loop_count, 1)
        self.assertEqual(metrics.cyclomatic_complexity, 2.0)  # 1 decision + 1
        self.assertEqual(metrics.decision_points, 1)

    def test_nested_operators(self):
        """Test complexity of nested operators."""
        model = parse_powl_model_string("X(A, X(B, C))")
        metrics = calculate_complexity_metrics(model)

        self.assertEqual(metrics.xor_count, 2)
        self.assertEqual(metrics.nesting_depth, 2)
        self.assertEqual(metrics.cyclomatic_complexity, 3.0)  # 2 decisions + 1

    def test_partial_order(self):
        """Test complexity of partial order."""
        model = parse_powl_model_string("PO=(nodes={A, B, C}, order={A-->B, B-->C})")
        metrics = calculate_complexity_metrics(model)

        self.assertEqual(metrics.partial_order_count, 1)
        self.assertEqual(metrics.activity_count, 3)
        self.assertGreater(metrics.total_edges, 0)

    def test_operator_diversity(self):
        """Test operator diversity calculation."""
        # Single operator type
        model1 = parse_powl_model_string("X(A, B)")
        metrics1 = calculate_complexity_metrics(model1)
        self.assertEqual(metrics1.operator_diversity, 0.0)  # Only XOR

        # Multiple operator types
        model2 = parse_powl_model_string("X(A, *(B, C))")
        metrics2 = calculate_complexity_metrics(model2)
        self.assertGreater(metrics2.operator_diversity, 0)

    def test_structuredness(self):
        """Test block-structuredness calculation."""
        # Simple sequence is block-structured
        model = parse_powl_model_string("PO=(nodes={A, B}, order={A-->B})")
        metrics = calculate_complexity_metrics(model)
        self.assertEqual(metrics.is_block_structured, True)
        self.assertEqual(metrics.structuredness, 1.0)

    def test_connectance(self):
        """Test connectance calculation."""
        model = parse_powl_model_string("PO=(nodes={A, B}, order={A-->B})")
        metrics = calculate_complexity_metrics(model)

        self.assertGreater(metrics.connectance, 0)
        self.assertLessEqual(metrics.connectance, 1)

    def test_comparison(self):
        """Test comparing two complexity metrics."""
        model1 = parse_powl_model_string("A")
        model2 = parse_powl_model_string("X(A, B)")

        metrics1 = calculate_complexity_metrics(model1)
        metrics2 = calculate_complexity_metrics(model2)

        comparison = compare_complexity(metrics1, metrics2)

        self.assertEqual(comparison["simpler"], False)  # model2 is more complex
        self.assertGreater(comparison["cyclomatic_complexity_delta"], 0)

    def test_timestamp_included(self):
        """Test that timestamp is included by default."""
        model = parse_powl_model_string("A")
        metrics = calculate_complexity_metrics(model)

        self.assertIsNotNone(metrics.timestamp)
        self.assertIn("T", metrics.timestamp)

    def test_timestamp_excluded(self):
        """Test that timestamp can be excluded."""
        model = parse_powl_model_string("A")
        metrics = calculate_complexity_metrics(model, include_timestamp=False)

        self.assertIsNone(metrics.timestamp)

    def test_model_hash(self):
        """Test that model hash is generated."""
        model = parse_powl_model_string("A")
        metrics = calculate_complexity_metrics(model)

        self.assertIsNotNone(metrics.model_hash)
        self.assertEqual(len(metrics.model_hash), 8)

    def test_hash_consistency(self):
        """Test that hash is consistent for same model."""
        model = parse_powl_model_string("X(A, B)")
        metrics1 = calculate_complexity_metrics(model)
        metrics2 = calculate_complexity_metrics(model)

        self.assertEqual(metrics1.model_hash, metrics2.model_hash)

    def test_hash_different_models(self):
        """Test that hash differs for different models."""
        model1 = parse_powl_model_string("X(A, B)")
        model2 = parse_powl_model_string("X(A, C)")

        metrics1 = calculate_complexity_metrics(model1)
        metrics2 = calculate_complexity_metrics(model2)

        self.assertNotEqual(metrics1.model_hash, metrics2.model_hash)


if __name__ == '__main__':
    unittest.main()
