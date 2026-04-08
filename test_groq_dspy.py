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
Test Groq with DSPy via litellm.

Make sure GROQ_API_KEY is set in your environment.
"""

import os
import dspy

# Configure litellm with Groq
# DSPy uses litellm under the hood for various LLM providers

def setup_groq_litellm():
    """Configure Groq API key for litellm/DSPy."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set!")

    # Set up environment for litellm to find Groq
    os.environ["GROQ_API_KEY"] = api_key

    # Configure DSPy to use litellm with Groq
    # litellm model format: "groq/model_name"
    lm = dspy.LM(
        model="groq/openai/gpt-oss-20b",  # GPT-OSS models
        api_key=api_key,
        api_base="https://api.groq.com/openai/v1"
    )

    return lm

def main():
    # Set up Groq via litellm
    lm = setup_groq_litellm()

    # Set as default language model
    dspy.configure(lm=lm)

    # Test basic completion
    print("Testing Groq + DSPy + litellm...")

    # Define a simple signature
    class GenerateAnswer(dspy.Signature):
        """Answer questions with short factoid answers."""

        question = dspy.InputField(desc="Question to answer")
        answer = dspy.OutputField(desc="Answer to the question")

    # Create and run a predictor
    predictor = dspy.Predict(GenerateAnswer)
    result = predictor(question="What is the capital of France?")

    print(f"\nQuestion: What is the capital of France?")
    print(f"Answer: {result.answer}")

    # Test with a more complex question
    result2 = predictor(question="Explain process mining in one sentence.")
    print(f"\nQuestion: Explain process mining in one sentence.")
    print(f"Answer: {result2.answer}")

    print("\n✅ Groq is working with DSPy via litellm!")

if __name__ == "__main__":
    main()
