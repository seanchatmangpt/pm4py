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

'''
Unit tests for YAWL export functionality.

Tests cover:
- POWL to YAWL object model conversion
- YAWL XML serialization
- Pattern mappings (sequence, XOR, parallel, loop, partial order)
- CLI integration
'''

import unittest
import tempfile
import os
from pm4py.objects.powl.obj import Transition, OperatorPOWL, StrictPartialOrder, Sequence
from pm4py.objects.process_tree.obj import Operator
from pm4py.objects.yawl.obj import YAWLSpecification, YAWLTask, YAWLFlow
from pm4py.objects.conversion.yawl.converter import apply as convert_to_yawl_func
from pm4py.objects.yawl.exporter.exporter import serialize as yawl_serialize_func
import pm4py


class TestPOWLToYAWLConversion(unittest.TestCase):
    """Test POWL to YAWL object model conversion."""

    def test_powl_to_yawl_sequence(self):
        """Test conversion of simple sequence."""
        # Create sequence: A -> B -> C
        A = Transition('A')
        B = Transition('B')
        C = Transition('C')
        model = Sequence([A, B, C])

        yawl = convert_to_yawl_func(model)

        self.assertIsInstance(yawl, YAWLSpecification)
        self.assertIsNotNone(yawl.root_decomposition())

        root = yawl.root_decomposition()
        # Should have 3 tasks for A, B, C
        self.assertGreaterEqual(len(root.tasks), 3)

        # Check task names
        task_names = [task.name for task in root.tasks]
        self.assertIn("A", task_names)
        self.assertIn("B", task_names)
        self.assertIn("C", task_names)

    def test_powl_to_yawl_xor(self):
        """Test conversion of XOR choice."""
        # Create XOR: X(A, B)
        A = Transition('A')
        B = Transition('B')
        model = OperatorPOWL(Operator.XOR, [A, B])

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        # Should have tasks for A and B
        task_names = [task.name for task in root.tasks]
        self.assertIn("A", task_names)
        self.assertIn("B", task_names)

        # Check flows exist
        self.assertGreater(len(root.flows), 0)

    def test_powl_to_yawl_parallel(self):
        """Test conversion of parallel split using partial order."""
        # Create parallel: A || B (partial order with no edges)
        A = Transition('A')
        B = Transition('B')
        model = StrictPartialOrder([A, B])
        # No edges means they can execute in parallel

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        task_names = [task.name for task in root.tasks]
        self.assertIn("A", task_names)
        self.assertIn("B", task_names)

    def test_powl_to_yawl_loop(self):
        """Test conversion of loop structure."""
        # Create loop: LOOP(A, B)
        A = Transition('A')
        B = Transition('B')
        model = OperatorPOWL(Operator.LOOP, [A, B])

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        # Loop should create flows
        self.assertGreater(len(root.flows), 0)

    def test_powl_to_yawl_single_activity(self):
        """Test conversion of single activity."""
        model = Transition('A')
        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        self.assertEqual(len([t for t in root.tasks if t.name == "A"]), 1)


class TestYAWLXMLSerialization(unittest.TestCase):
    """Test YAWL XML serialization."""

    def test_yawl_xml_output(self):
        """Test XML serialization produces valid XML."""
        A = Transition('A')
        B = Transition('B')
        model = Sequence([A, B])

        yawl = convert_to_yawl_func(model)
        xml_str = yawl_serialize_func(yawl)

        # Check XML structure
        self.assertIn("<specification", xml_str)
        self.assertIn("xmlns=\"http://www.yawlfoundation.org/yawlschema\"", xml_str)
        self.assertIn("<decomposition", xml_str)
        self.assertIn("<task", xml_str)

    def test_yawl_xml_metadata(self):
        """Test metadata is included in XML."""
        A = Transition('A')
        B = Transition('B')
        model = Sequence([A, B])

        yawl = convert_to_yawl_func(model)
        xml_str = yawl_serialize_func(yawl)

        # Check metadata elements
        self.assertIn("<title>", xml_str)
        self.assertIn("<version>", xml_str)
        self.assertIn("<author>", xml_str)

    def test_yawl_xml_task_names(self):
        """Test task names are preserved in XML."""
        A = Transition('A')
        B = Transition('B')
        C = Transition('C')
        model = Sequence([A, B, C])

        yawl = convert_to_yawl_func(model)
        xml_str = yawl_serialize_func(yawl)

        # Check activity names in XML
        self.assertIn("A", xml_str)
        self.assertIn("B", xml_str)
        self.assertIn("C", xml_str)

    def test_yawl_xml_pretty_print(self):
        """Test pretty-printing produces readable output."""
        A = Transition('A')
        B = Transition('B')
        model = Sequence([A, B])

        yawl = convert_to_yawl_func(model)
        xml_str = yawl_serialize_func(yawl)

        # Pretty-printed XML should have newlines
        self.assertIn("\n", xml_str)

        # Should have proper indentation
        lines = xml_str.split("\n")
        non_empty = [l for l in lines if l.strip()]
        self.assertGreater(len(non_empty), 5)


class TestYAWLWriteFunction(unittest.TestCase):
    """Test write_yawl() function."""

    def test_write_yawl_file(self):
        """Test writing YAWL to file."""
        A = Transition('A')
        B = Transition('B')
        model = Sequence([A, B])

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yawl") as f:
            temp_path = f.name

        try:
            pm4py.write_yawl(model, temp_path)
            self.assertTrue(os.path.exists(temp_path))

            # Read and check content
            with open(temp_path, "r") as f:
                content = f.read()
            self.assertIn("<specification", content)
            self.assertIn("A", content)
            self.assertIn("B", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_write_yawl_auto_extension(self):
        """Test .yawl extension is added automatically."""
        A = Transition('A')
        B = Transition('B')
        model = Sequence([A, B])

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            temp_path = f.name

        # Remove the temp file but keep the path
        if os.path.exists(temp_path):
            os.remove(temp_path)

        try:
            # Write without .yawl extension
            base_path = temp_path.replace(".tmp", "")
            pm4py.write_yawl(model, base_path)

            # Check .yawl file was created
            yawl_path = base_path + ".yawl"
            self.assertTrue(os.path.exists(yawl_path))
        finally:
            for ext in ["", ".yawl"]:
                path = temp_path.replace(".tmp", ext)
                if os.path.exists(path):
                    os.remove(path)


class TestPublicAPI(unittest.TestCase):
    """Test public API functions."""

    def test_convert_to_yawl_function(self):
        """Test pm4py.convert_to_yawl() function."""
        A = Transition('A')
        B = Transition('B')
        model = Sequence([A, B])

        yawl = pm4py.convert_to_yawl(model)

        self.assertIsInstance(yawl, YAWLSpecification)
        self.assertIsNotNone(yawl.root_decomposition())

    def test_convert_to_yawl_from_powl(self):
        """Test convert_to_yawl accepts POWL model."""
        A = Transition('A')
        B = Transition('B')
        model = OperatorPOWL(Operator.XOR, [A, B])

        yawl = pm4py.convert_to_yawl(model)

        root = yawl.root_decomposition()
        self.assertGreater(len(root.tasks), 0)


class TestPatternMappings(unittest.TestCase):
    """Test pattern mappings from the 43 workflow patterns."""

    def test_pattern_1_sequence(self):
        """Test Pattern 1: Sequence."""
        A = Transition('A')
        B = Transition('B')
        C = Transition('C')
        model = Sequence([A, B, C])

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        task_names = [t.name for t in root.tasks if t.name]

        self.assertEqual(task_names, ["A", "B", "C"])

    def test_pattern_2_parallel_split(self):
        """Test Pattern 2: Parallel Split (via partial order)."""
        A = Transition('A')
        B = Transition('B')
        # Parallel split: no ordering constraint
        model = StrictPartialOrder([A, B])

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        # Both tasks should exist
        task_names = [t.name for t in root.tasks if t.name]
        self.assertIn("A", task_names)
        self.assertIn("B", task_names)

    def test_pattern_4_exclusive_choice(self):
        """Test Pattern 4: Exclusive Choice (XOR)."""
        A = Transition('A')
        B = Transition('B')
        model = OperatorPOWL(Operator.XOR, [A, B])

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        # Should have tasks for A and B
        task_names = [t.name for t in root.tasks if t.name]
        self.assertIn("A", task_names)
        self.assertIn("B", task_names)

    def test_pattern_15_structured_loop(self):
        """Test Pattern 15: Structured Loop."""
        A = Transition('A')
        B = Transition('B')
        model = OperatorPOWL(Operator.LOOP, [A, B])

        yawl = convert_to_yawl_func(model)

        root = yawl.root_decomposition()
        # Loop creates flows
        self.assertGreater(len(root.flows), 0)


if __name__ == "__main__":
    unittest.main()
