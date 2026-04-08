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
Test GPT-OSS-20B model on Groq via DSPy + litellm.

This demonstrates using the openai/gpt-oss-20b model hosted on Groq.
"""

import os
import dspy

def setup_gpt_oss_20b():
    """Configure GPT-OSS-20B on Groq."""
    from groq_litellm_config import configure_groq

    # For OpenAI models hosted on Groq, use custom_llm_provider='groq'
    lm = configure_groq(
        model="gpt-oss-20b",  # or use full "openai/gpt-oss-20b"
        custom_llm_provider="groq",  # Required for openai/* models on Groq
        temperature=0.7,
        max_tokens=1024
    )

    return lm

def main():
    print("Testing GPT-OSS-20B on Groq + DSPy + litellm\n")

    # Configure
    lm = setup_gpt_oss_20b()
    dspy.configure(lm=lm)

    # Test 1: Simple Q&A
    print("="*60)
    print("Test 1: Simple Q&A")
    print("="*60)

    class SimpleQA(dspy.Signature):
        """Answer questions concisely."""
        question = dspy.InputField(desc="Question")
        answer = dspy.OutputField(desc="Answer")

    qa = dspy.Predict(SimpleQA)

    questions = [
        "What is 2+2?",
        "What is the capital of France?",
        "Explain process mining in one sentence.",
    ]

    for q in questions:
        result = qa(question=q)
        print(f"\nQ: {q}")
        print(f"A: {result.answer}")

    # Test 2: Chain of Thought
    print("\n" + "="*60)
    print("Test 2: Chain of Thought Reasoning")
    print("="*60)

    class ReasoningQA(dspy.Signature):
        """Answer questions with reasoning."""
        question = dspy.InputField(desc="Question requiring reasoning")
        reasoning = dspy.OutputField(desc="Step-by-step reasoning")
        answer = dspy.OutputField(desc="Final answer")

    cot = dspy.ChainOfThought(ReasoningQA)

    result = cot(question="If a baker has 12 cookies and sells 5, then buys 7 more, how many cookies does the baker have?")
    print(f"\nQ: If a baker has 12 cookies and sells 5, then buys 7 more, how many cookies does the baker have?")
    print(f"Reasoning: {result.reasoning}")
    print(f"Answer: {result.answer}")

    # Test 3: Process Mining specific
    print("\n" + "="*60)
    print("Test 3: Process Mining Domain Knowledge")
    print("="*60)

    pm_questions = [
        "What is token-based replay conformance checking?",
        "Explain the difference between DFG and Petri nets.",
        "What is the alpha miner algorithm?",
    ]

    for q in pm_questions:
        result = qa(question=q)
        print(f"\nQ: {q}")
        print(f"A: {result.answer}")

    print("\n" + "="*60)
    print("✅ GPT-OSS-20B is working perfectly!")
    print("="*60)

if __name__ == "__main__":
    main()
