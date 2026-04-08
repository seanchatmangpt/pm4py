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
Groq + DSPy + litellm Configuration Examples

This module shows various ways to configure Groq with DSPy using litellm.
The GROQ_API_KEY should be set in your environment.
"""

import os
import dspy
from typing import Optional

# Available Groq models as of 2026-04
GROQ_MODELS = {
    # OpenAI models hosted on Groq
    "gpt-oss-20b": "groq/openai/gpt-oss-20b",
    "gpt-oss-120b": "groq/openai/gpt-oss-120b",
    "gpt-oss-safeguard-20b": "groq/openai/gpt-oss-safeguard-20b",
}


def get_groq_api_key() -> str:
    """Get Groq API key from environment."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable not set!\n"
            "Set it with: export GROQ_API_KEY='your-key-here'"
        )
    return api_key


def configure_groq(
    model: str = "gpt-oss-20b",
    temperature: float = 0.0,
    max_tokens: int = 1024,
    api_base: Optional[str] = None,
) -> dspy.LM:
    """
    Configure DSPy to use Groq via litellm.

    Args:
        model: Model name (default: gpt-oss-20b)
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens in response
        api_base: Custom API base URL (default: Groq's OpenAI-compatible endpoint)

    Returns:
        Configured dspy.LM instance

    Example:
        >>> # GPT-OSS-20B (recommended, fastest)
        >>> lm = configure_groq(model="gpt-oss-20b", temperature=0.0)
        >>> dspy.configure(lm=lm)
        >>>
        >>> # GPT-OSS-120B (higher quality)
        >>> lm = configure_groq(
        ...     model="gpt-oss-120b"
        ... )
    """
    api_key = get_groq_api_key()

    # Map model name to litellm format
    litellm_model = GROQ_MODELS.get(model, f"groq/{model}")

    # Default API base for Groq (OpenAI-compatible)
    if api_base is None:
        api_base = "https://api.groq.com/openai/v1"

    # Build LM kwargs
    lm_kwargs = {
        "model": litellm_model,
        "api_key": api_key,
        "api_base": api_base,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    lm = dspy.LM(**lm_kwargs)

    return lm


def configure_groq_with_cache(
    model: str = "gpt-oss-20b",
    cache_dir: Optional[str] = None,
    **kwargs
) -> dspy.LM:
    """
    Configure Groq with response caching enabled.

    Caching reduces API costs and latency for repeated queries.

    Args:
        model: Model name
        cache_dir: Directory for cache (default: ./cache/dspy)
        **kwargs: Additional arguments passed to configure_groq()

    Returns:
        Configured dspy.LM instance with caching
    """
    if cache_dir is None:
        cache_dir = "./cache/dspy"

    os.makedirs(cache_dir, exist_ok=True)

    lm = configure_groq(model=model, **kwargs)

    # DSPy's LM has built-in caching support
    # Set cache directory in environment for litellm
    os.environ["DSPY_CACHEDIR"] = cache_dir

    return lm


def quick_test(model: str = "gpt-oss-20b") -> None:
    """
    Quick test to verify Groq is working.

    Args:
        model: Groq model to test
    """
    print(f"Testing Groq model: {model}")

    lm = configure_groq(model=model, temperature=0.3)
    dspy.configure(lm=lm)

    class QuickQuestion(dspy.Signature):
        """Ask a simple question."""

        question = dspy.InputField(desc="Question to answer")
        answer = dspy.OutputField(desc="Answer")

    predictor = dspy.Predict(QuickQuestion)

    test_questions = [
        "What is 2+2?",
        "Name a Python process mining library.",
        "What does Groq specialize in?",
    ]

    for q in test_questions:
        result = predictor(question=q)
        print(f"\nQ: {q}")
        print(f"A: {result.answer}")

    print(f"\n✅ {model} is working!")


# Example: Process Mining Assistant
class ProcessMiningAssistant(dspy.Module):
    """A simple process mining Q&A assistant."""

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought("process_question -> process_answer")

    def forward(self, question: str) -> str:
        """Answer a process mining question."""
        result = self.generate(process_question=question)
        return result.process_answer


def create_process_mining_assistant(
    model: str = "gpt-oss-20b"
) -> ProcessMiningAssistant:
    """
    Create a process mining assistant powered by Groq.

    Args:
        model: Groq model to use

    Returns:
        Configured ProcessMiningAssistant instance

    Example:
        >>> assistant = create_process_mining_assistant()
        >>> answer = assistant("What is conformance checking?")
        >>> print(answer)
    """
    lm = configure_groq(model=model, temperature=0.5)
    dspy.configure(lm=lm)

    return ProcessMiningAssistant()


if __name__ == "__main__":
    # Run quick test
    quick_test(model="gpt-oss-20b")

    print("\n" + "="*60)
    print("Process Mining Assistant Demo")
    print("="*60)

    # Create and test process mining assistant
    assistant = create_process_mining_assistant()

    pm_questions = [
        "What is process discovery?",
        "Explain token-based replay conformance checking.",
        "What is the difference between DFG and Petri net?",
    ]

    for q in pm_questions:
        print(f"\nQ: {q}")
        answer = assistant(q)
        print(f"A: {answer}")
