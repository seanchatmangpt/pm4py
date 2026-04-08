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

"""
Test PM4Py with Groq LLM integration.

This demonstrates using Groq's fast inference with PM4Py's built-in LLM features.
"""

import pm4py
import os

def test_basic_groq_query():
    """Test basic Groq query."""
    print("="*60)
    print("Test 1: Basic Groq Query")
    print("="*60)

    response = pm4py.llm.groq_query("What is process mining in one sentence?")
    print(f"Response: {response}\n")


def test_groq_with_abstraction():
    """Test Groq with process abstraction."""
    print("="*60)
    print("Test 2: Groq with Process Abstraction")
    print("="*60)

    # Load sample log
    log = pm4py.read_xes("tests/input_data/running-example.xes")

    # Abstract the process to text
    dfg_text = pm4py.llm.abstract_dfg(log, max_len=2000)
    print(f"DFG Abstraction:\n{dfg_text[:200]}...\n")

    # Query Groq with process context
    prompt = f"Analyze this process model:\n\n{dfg_text}\n\nWhat are the main activities?"
    response = pm4py.llm.groq_query(prompt)
    print(f"Analysis: {response}\n")


def test_groq_clustering():
    """Test Groq-based clustering."""
    print("="*60)
    print("Test 3: Groq-based Clustering")
    print("="*60)

    log = pm4py.read_xes("tests/input_data/running-example.xes")

    # Perform clustering using Groq
    clusters = pm4py.llm.clustering(
        log,
        executor=pm4py.llm.groq_query,
        max_len=2000
    )

    print(f"Found {len(clusters)} clusters:")
    for name, df in clusters:
        print(f"  - {name}: {len(df)} cases")


def test_groq_nlp_to_sql():
    """Test natural language to SQL with Groq."""
    print("="*60)
    print("Test 4: Natural Language to SQL")
    print("="*60)

    log = pm4py.read_xes("tests/input_data/running-example.xes")

    # Convert natural language to SQL query
    result = pm4py.llm.nlp_to_log_query(
        log,
        "How many cases are in the event log?",
        executor=pm4py.llm.groq_query,
        api_key=os.environ.get("GROQ_API_KEY")
    )

    print(f"Result:\n{result}")


def test_groq_gpt_oss_20b():
    """Test Groq with GPT-OSS-20B model."""
    print("="*60)
    print("Test 5: Groq with GPT-OSS-20B Model")
    print("="*60)

    response = pm4py.llm.groq_query(
        "Explain token-based replay conformance checking in process mining.",
        model="openai/gpt-oss-20b",
        custom_llm_provider="groq"  # Required for openai/* models on Groq
    )
    print(f"Response: {response}\n")


def main():
    """Run all tests."""
    print("Testing PM4Py + Groq Integration\n")

    try:
        test_basic_groq_query()
        test_groq_with_abstraction()
        test_groq_clustering()
        test_groq_nlp_to_sql()
        test_groq_gpt_oss_20b()

        print("\n" + "="*60)
        print("✅ All PM4Py + Groq tests passed!")
        print("="*60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
