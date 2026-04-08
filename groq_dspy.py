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
Groq DSPy Wrapper

A simple wrapper for using Groq with DSPy via litellm.
"""

import os
from typing import Optional
import dspy


class GroqDSPy:
    """
    Wrapper for Groq + DSPy integration.

    Example:
        >>> groq = GroqDSPy()  # Uses GROQ_API_KEY from environment
        >>> groq.configure()
        >>>
        >>> # Define your DSPy module
        >>> class MyModule(dspy.Module):
        ...     def forward(self, text):
        ...         return dspy.Predict("text -> output")(text=text)
        >>>
        >>> # Use it
        >>> module = MyModule()
        >>> result = module("Hello, process mining!")
    """

    DEFAULT_MODEL = "openai/gpt-oss-20b"
    DEFAULT_API_BASE = "https://api.groq.com/openai/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        api_base: str = DEFAULT_API_BASE,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize Groq DSPy wrapper.

        Args:
            api_key: Groq API key (default: from GROQ_API_KEY env var)
            model: Model name (default: openai/gpt-oss-20b)
            api_base: API base URL
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            cache_dir: Cache directory for responses
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment or passed as parameter")

        self.model = f"groq/{model}" if not model.startswith("groq/") else model
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.cache_dir = cache_dir

        self._lm = None

    def configure(self) -> dspy.LM:
        """
        Configure DSPy with Groq.

        Returns:
            Configured dspy.LM instance
        """
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
            os.environ["DSPY_CACHEDIR"] = self.cache_dir

        self._lm = dspy.LM(
            model=self.model,
            api_key=self.api_key,
            api_base=self.api_base,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        dspy.configure(lm=self._lm)
        return self._lm

    def test(self) -> bool:
        """
        Test the connection.

        Returns:
            True if successful, raises exception otherwise
        """
        if not self._lm:
            self.configure()

        class TestSignature(dspy.Signature):
            question = dspy.InputField(desc="Test question")
            answer = dspy.OutputField(desc="Answer")

        predictor = dspy.Predict(TestSignature)
        result = predictor(question="What is 2+2?")

        return "4" in result.answer or "four" in result.answer.lower()

    def create_predictor(
        self,
        signature: type[dspy.Signature],
        **kwargs
    ) -> dspy.Predict:
        """
        Create a DSPy predictor with the configured Groq LM.

        Args:
            signature: DSPy signature class
            **kwargs: Additional arguments for dspy.Predict

        Returns:
            Configured predictor
        """
        if not self._lm:
            self.configure()

        return dspy.Predict(signature, **kwargs)

    def create_chain_of_thought(
        self,
        signature: type[dspy.Signature],
        **kwargs
    ) -> dspy.ChainOfThought:
        """
        Create a Chain-of-Thought predictor.

        Args:
            signature: DSPy signature class
            **kwargs: Additional arguments for dspy.ChainOfThought

        Returns:
            Configured ChainOfThought predictor
        """
        if not self._lm:
            self.configure()

        return dspy.ChainOfThought(signature, **kwargs)


# Convenience functions

def quick_configure(
    model: str = GroqDSPy.DEFAULT_MODEL,
    temperature: float = 0.7,
) -> GroqDSPy:
    """
    Quick configure Groq for DSPy.

    Args:
        model: Groq model name
        temperature: Sampling temperature

    Returns:
        Configured GroqDSPy instance

    Example:
        >>> groq = quick_configure(model="gpt-oss-20b")
        >>> predictor = groq.create_predictor(MySignature)
    """
    groq = GroqDSPy(model=model, temperature=temperature)
    groq.configure()
    return groq


def test_groq() -> None:
    """Test Groq connection with a simple query."""
    groq = GroqDSPy()
    groq.configure()

    if groq.test():
        print("✅ Groq is working with DSPy!")
    else:
        print("❌ Groq test failed")


if __name__ == "__main__":
    # Run test
    test_groq()

    # Example usage
    print("\n" + "="*50)
    print("Example: Simple Q&A")
    print("="*50)

    groq = quick_configure(temperature=0.3)

    class SimpleQA(dspy.Signature):
        """Answer questions concisely."""
        question = dspy.InputField(desc="Question to answer")
        answer = dspy.OutputField(desc="Concise answer")

    predictor = groq.create_predictor(SimpleQA)

    result = predictor(question="What is PM4Py?")
    print(f"\nQ: What is PM4Py?")
    print(f"A: {result.answer}")
