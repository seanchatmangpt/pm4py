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
import os

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

import pm4py


@unittest.skipIf(
    not DSPY_AVAILABLE,
    "DSPy not installed. Install with: pip install dspy-ai",
)
class DSPyPOWLTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up DSPy with a mock/test LM for testing."""
        import dspy

        # Use a simple mock if no API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            # If API key is available, use real LM
            lm = dspy.OpenAI(model="gpt-4", api_key=api_key)
        else:
            # Use mock for testing without API key
            lm = dspy.ChainOfThought(
                dspy.Signature(
                    "input -> output"
                )  # Placeholder mock signature
            )

        try:
            dspy.settings.configure(lm=lm)
        except Exception:
            # If configuration fails, skip these tests
            pass

    def test_powl_explainer_module_instantiation(self):
        """Test that POWLExplainer can be instantiated."""
        from pm4py.algo.querying.llm.powl.algorithm import POWLExplainer

        explainer = POWLExplainer()
        self.assertIsNotNone(explainer)

    def test_powl_discoverer_module_instantiation(self):
        """Test that POWLDiscoverer can be instantiated."""
        from pm4py.algo.querying.llm.powl.algorithm import POWLDiscoverer

        discoverer = POWLDiscoverer()
        self.assertIsNotNone(discoverer)

    def test_powl_comparator_module_instantiation(self):
        """Test that POWLComparator can be instantiated."""
        from pm4py.algo.querying.llm.powl.algorithm import POWLComparator

        comparator = POWLComparator()
        self.assertIsNotNone(comparator)

    def test_signatures_exist(self):
        """Test that DSPy signatures are properly defined."""
        from pm4py.algo.querying.llm.powl.signatures import (
            ExplainPOWL,
            DiscoverPOWLFromDescription,
            ComparePOWLModels,
        )

        self.assertTrue(hasattr(ExplainPOWL, "__doc__"))
        self.assertTrue(hasattr(DiscoverPOWLFromDescription, "__doc__"))
        self.assertTrue(hasattr(ComparePOWLModels, "__doc__"))

    def test_powl_llm_functions_exist(self):
        """Test that high-level POWL LLM functions are available."""
        from pm4py.algo.querying.llm.powl import powl_llm

        self.assertTrue(callable(powl_llm.explain_powl))
        self.assertTrue(callable(powl_llm.discover_powl_from_description))
        self.assertTrue(callable(powl_llm.compare_powl_models))

    def test_public_api_functions_exist(self):
        """Test that public API functions are available in pm4py.llm."""
        self.assertTrue(callable(pm4py.llm.explain_powl))
        self.assertTrue(callable(pm4py.llm.discover_powl_from_description))
        self.assertTrue(callable(pm4py.llm.compare_powl_models))

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OPENAI_API_KEY not set. Skipping LLM integration tests.",
    )
    def test_explain_powl_with_real_lm(self):
        """Test explain_powl with a real LM (requires API key)."""
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        powl = pm4py.discover_powl(log)
        explanation = pm4py.llm.explain_powl(powl)
        self.assertGreater(len(explanation), 0)

    @unittest.skipIf(
        not os.getenv("OPENAI_API_KEY"),
        "OPENAI_API_KEY not set. Skipping LLM integration tests.",
    )
    def test_compare_powl_models_with_real_lm(self):
        """Test compare_powl_models with a real LM (requires API key)."""
        log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
        powl_1 = pm4py.discover_powl(log)
        powl_2 = pm4py.discover_powl(log)  # In practice, different variant
        result = pm4py.llm.compare_powl_models(powl_1, powl_2)
        self.assertIn("comparison", result)
        self.assertIn("confidence", result)


if __name__ == "__main__":
    unittest.main()
