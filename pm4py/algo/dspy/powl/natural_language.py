"""
Natural Language to POWL Discovery using DSPy.

This module uses DSPy with Groq gpt-oss-20b to generate POWL models
from natural language descriptions.

Supports all POWL patterns:
- LOOP: *(A) or *(A, B)
- INTERLEAVING: <>(A, B, ...)
- XOR (Exclusive Choice): X(A, B, ...)
- PARALLEL: +(A, B, ...) or PO=(nodes={...}, order={})
- SEQUENCE: ->(A, B, ...)
- OR (Inclusive Choice): O(A, B, ...)
- PARTIAL ORDER: PO=(nodes={...}, order={...})
"""

import os
from typing import Any, Dict, List, Optional

try:
    import dspy
    from groq import Groq
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    dspy = None
    Groq = None


# Default model configuration
DEFAULT_MODEL = "groq/openai/gpt-oss-20b"
DEFAULT_API_KEY = os.environ.get("GROQ_API_KEY")


# DSPy 2.x Signatures
if DSPY_AVAILABLE:
    class POWLGenerationSignature(dspy.Signature):
        """Generate a POWL model string from a natural language process description."""
        task: str = dspy.InputField(desc="Natural language process description or task")
        domain: str = dspy.InputField(desc="Process domain (manufacturing, finance, incident_response, etc.)")
        powl_model: str = dspy.OutputField(desc="Valid POWL model string using SEQ, X, PAR, *, <>, OR operators")
        explanation: str = dspy.OutputField(desc="Explanation of the POWL structure")

    class POWLRefinementSignature(dspy.Signature):
        """Refine a POWL model based on validation issues."""
        original_powl: str = dspy.InputField(desc="Original POWL model string")
        issues: str = dspy.InputField(desc="Validation issues found in the model")
        refined_powl: str = dspy.OutputField(desc="Refined POWL model string that addresses the issues")

    # Module-level PowlPredictor class (exposed for public use)
    class PowlPredictor(dspy.Module):
        """POWL generation module using DSPy 2.x ChainOfThought.

        This is the main public class for generating POWL models from natural language.
        """

        def __init__(self, model: str = DEFAULT_MODEL, max_tokens: int = 4096):
            """Initialize the POWL predictor.

            Args:
                model: DSPy model identifier (default: groq/openai/gpt-oss-20b)
                max_tokens: Maximum tokens for generation (default: 4096)
            """
            super().__init__()
            self.model = model
            self.max_tokens = max_tokens

            # Use ChainOfThought for better reasoning
            self.predictor = dspy.ChainOfThought(POWLGenerationSignature)
            self.refiner = dspy.ChainOfThought(POWLRefinementSignature)

        def forward(self, task: str, domain: str = "general") -> dspy.Prediction:
            """Generate POWL from task description using DSPy 2.x.

            Args:
                task: Natural language process description or task
                domain: Process domain (optional, default: 'general')

            Returns:
                dspy.Prediction with powl_model and explanation attributes
            """
            try:
                # Call the predictor with the signature fields
                result = self.predictor(
                    task=task,
                    domain=domain or "general"
                )

                # Extract the generated POWL
                powl_str = result.powl_model if hasattr(result, 'powl_model') else str(result)
                explanation = result.explanation if hasattr(result, 'explanation') else ""

                return dspy.Prediction(
                    powl=powl_str,
                    explanation=explanation
                )
            except Exception as e:
                # Fallback to empty result on error
                return dspy.Prediction(
                    powl="",
                    explanation=f"Error: {str(e)}"
                )

        def refine(self, original_powl: str, issues: str) -> str:
            """Refine a POWL model based on validation issues.

            Args:
                original_powl: Original POWL model string
                issues: Description of validation issues

            Returns:
                Refined POWL model string, or original if refinement fails
            """
            try:
                result = self.refiner(
                    original_powl=original_powl,
                    issues=issues
                )
                refined = result.refined_powl if hasattr(result, 'refined_powl') else original_powl
                return refined if refined else original_powl
            except Exception:
                return original_powl


def _setup_dspy(model: str = DEFAULT_MODEL) -> bool:
    """Configure DSPy with Groq model.

    Returns True if setup successful, False otherwise.
    """
    if not DSPY_AVAILABLE:
        return False

    if not DEFAULT_API_KEY:
        return False

    # Configure Groq for DSPy (dspy >= 2.5 uses dspy.LM, not dspy.Groq)
    try:
        lm = dspy.LM(model=model, api_key=DEFAULT_API_KEY)
        dspy.configure(lm=lm)
        return True
    except Exception as _e:
        import logging as _logging
        _logging.getLogger(__name__).warning("_setup_dspy failed: %s: %s", type(_e).__name__, _e)
        return False


def generate_powl_from_text(
    process_description: str,
    model: str = DEFAULT_MODEL,
    max_refinements: int = 2,
    use_demos: bool = True,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a POWL model from natural language description.

    Uses DSPy with Groq gpt-oss-20b to generate a POWL model string,
    then validates the result with a syntax checker and semantic judge.

    Parameters
    ----------
    process_description : str
        Natural language description of the business process
    model : str
        LLM model identifier (default: groq/openai/gpt-oss-20b)
    max_refinements : int
        Maximum number of judge-and-refine iterations (default: 2)
    use_demos : bool
        Whether to use few-shot examples (default: True)
    domain : str, optional
        Domain context for the process (e.g., 'healthcare', 'finance')

    Returns
    -------
    dict with keys:
        - powl: POWL model string
        - verdict: Boolean indicating if model passed validation
        - reasoning: Judge's reasoning
        - refinements: Number of refinement iterations performed
        - analysis: Optional structural analysis
        - feedback: Optional improvement suggestions

    Raises
    ------
    RuntimeError
        If DSPy is not available or GROQ_API_KEY is not set
    ValueError
        If process_description is empty

    Examples
    --------
    >>> result = generate_powl_from_text("Approve purchase orders under $1000")
    >>> print(result["powl"])
    'X (approve, reject)'
    >>> print(result["verdict"])
    True
    """
    if not DSPY_AVAILABLE:
        raise RuntimeError(
            "DSPy is not installed. Install with: pip install dspy groq"
        )

    if not DEFAULT_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY environment variable is not set. "
            "Get your API key from https://console.groq.com/"
        )

    if not process_description or not process_description.strip():
        raise ValueError("process_description cannot be empty")

    # Build the LM instance; use dspy.context() so the LM is scoped to this
    # call (async-safe — avoids "configure can only be called from the same
    # async task" error when multiple async tests run concurrently).
    try:
        _lm = dspy.LM(model=model, api_key=DEFAULT_API_KEY)
    except Exception as _e:
        raise RuntimeError(f"Failed to create LM for model {model}: {_e}") from _e

    with dspy.context(lm=_lm):
        return _generate_powl_from_text_inner(
            process_description, model, max_refinements, use_demos, domain
        )


def _generate_powl_from_text_inner(
    process_description: str,
    model: str = DEFAULT_MODEL,
    max_refinements: int = 2,
    use_demos: bool = True,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """Inner implementation of generate_powl_from_text within a dspy.context."""
    # Define DSPy 2.x signatures for validation
    class PowlValidatorSignature(dspy.Signature):
        """Validate POWL model syntax and semantics."""
        powl: str = dspy.InputField(desc="POWL model string to validate")
        description: str = dspy.InputField(desc="Original process description")
        is_valid: bool = dspy.OutputField(desc="Whether POWL is syntactically valid")
        verdict: bool = dspy.OutputField(desc="Overall verdict: structurally sound or not")
        reasoning: str = dspy.OutputField(desc="Explanation of the validation result")
        issues: str = dspy.OutputField(desc="List of issues found, if any")

    # Create POWL generator with few-shot examples
    generator = _create_powl_generator_v2(use_demos, model)

    # Generate initial POWL
    try:
        result = generator.forward(
            task=process_description,
            domain=domain or ""
        )
        powl_string = result.powl if hasattr(result, 'powl') else result.get("powl", "")
    except Exception as e:
        return {
            "powl": None,
            "verdict": False,
            "reasoning": f"Generation failed: {str(e)}",
            "refinements": 0,
            "analysis": None,
            "feedback": "Check the process description and try again."
        }

    # Validate the generated POWL using ChainOfThought
    validator = dspy.ChainOfThought(PowlValidatorSignature)

    for refinement in range(max_refinements + 1):
        try:
            validation = validator(
                powl=powl_string,
                description=process_description
            )

            # Extract boolean values safely
            is_valid = validation.is_valid if hasattr(validation, 'is_valid') else False
            verdict = validation.verdict if hasattr(validation, 'verdict') else False

            # Check if valid
            if is_valid and verdict:
                return {
                    "powl": powl_string,
                    "verdict": True,
                    "reasoning": getattr(validation, 'reasoning', ''),
                    "refinements": refinement,
                    "analysis": _analyze_powl_structure(powl_string),
                    "feedback": None
                }

            # If not the last refinement, try to improve
            if refinement < max_refinements:
                issues = getattr(validation, 'issues', '')
                refined = generator.refine(powl_string, issues)
                if refined and refined != powl_string:
                    powl_string = refined

        except Exception as e:
            # If validation fails, this is a serious issue
            if refinement == 0:
                return {
                    "powl": powl_string,
                    "verdict": False,
                    "reasoning": f"Validation error: {str(e)}",
                    "refinements": refinement,
                    "analysis": None,
                    "feedback": "The POWL model could not be validated."
                }

    # If we exhausted refinements without success
    return {
        "powl": powl_string,
        "verdict": False,
        "reasoning": "Could not generate a structurally sound POWL model within the refinement limit.",
        "refinements": max_refinements,
        "analysis": _analyze_powl_structure(powl_string),
        "feedback": "Try providing a more detailed description or breaking down the process into smaller steps."
    }


def _create_powl_generator(use_demos: bool = True) -> dspy.Module:
    """Create a DSPy module for POWL generation with few-shot examples.

    DEPRECATED: Use _create_powl_generator_v2 instead.
    Kept for backward compatibility.
    """
    return _create_powl_generator_v2(use_demos, DEFAULT_MODEL)


def _create_powl_generator_v2(use_demos: bool = True, model: str = DEFAULT_MODEL) -> "PowlPredictor":
    """Create a DSPy 2.x module for POWL generation with few-shot examples.

    This is a factory function that returns an instance of PowlPredictor
    with few-shot demonstrations wired in (if use_demos=True).

    Args:
        use_demos: Whether to wire few-shot examples (default: True)
        model: DSPy model identifier (default: groq/openai/gpt-oss-20b)

    Returns:
        PowlPredictor instance
    """
    if not DSPY_AVAILABLE:
        raise RuntimeError("DSPy is not available")

    # Create the predictor instance
    predictor = PowlPredictor(model=model)

    # Define few-shot examples for common patterns
    if use_demos:
        demos = [
            # Basic patterns
            dspy.Example(
                description="Sequential process: Submit expense report, then manager reviews it",
                domain="finance",
                powl_model='-> (\'Submit expense report\', \'Manager review\')',
                explanation="Simple sequence of two activities"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Choice: If amount < $100, auto-approve, else manager approval",
                domain="finance",
                powl_model="X ('Auto-approve', 'Manager approval')",
                explanation="Exclusive choice based on amount"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Loop: Repeat data validation until all fields are correct",
                domain="general",
                powl_model="* ('Validate fields', 'Submit data')",
                explanation="Do-while loop: validate fields, then submit, repeat if validation fails"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Single-node loop: Keep retrying the approval request",
                domain="general",
                powl_model="* ('Retry approval')",
                explanation="Single-node loop: repeat the same activity"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Parallel: Send email notification and update database simultaneously",
                domain="general",
                powl_model="+ ('Send email', 'Update database')",
                explanation="Parallel execution of two independent activities"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Partial order parallel: Payment processing and email notification can happen concurrently",
                domain="finance",
                powl_model="PO=(nodes={'Payment processing', 'Email notification'}, order={})",
                explanation="Partial order with no ordering constraint = parallel execution"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Interleaving: Task A and task B can happen in any order before proceeding",
                domain="general",
                powl_model="<> ('Task A', 'Task B')",
                explanation="Interleaved execution: A and B can execute in any order"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Inclusive choice: Approve with either signature OR manager override",
                domain="finance",
                powl_model="O ('Auto-approve', 'Manager override')",
                explanation="Inclusive choice: can execute either or both branches"
            ).with_inputs("description", "domain"),
            # Complex patterns
            dspy.Example(
                description="Nested choice with loop: Check document, if invalid fix it (loop), otherwise approve or reject",
                domain="document review",
                powl_model="X ('Document valid', * ('Fix issues', 'Reject'))",
                explanation="XOR with one branch being a LOOP for retry logic"
            ).with_inputs("description", "domain"),
            dspy.Example(
                description="Interleaved parallel steps: Prepare documents A and B in any order, then review",
                domain="general",
                powl_model="-> (<>(\'Prepare A\', \'Prepare B\'), 'Review')",
                explanation="Sequence with interleaved preparation step, then review"
            ).with_inputs("description", "domain"),
        ]

        # Wire in the demonstrations (up to 10)
        if hasattr(predictor.predictor, 'demos'):
            predictor.predictor.demos = demos[:10]

    return predictor


def _analyze_powl_structure(powl_string: str) -> Optional[Dict[str, Any]]:
    """Analyze the structure of a POWL model.

    Returns a dict with structure information.
    """
    if not powl_string:
        return None

    structure = {
        "operators": [],
        "activities": [],
        "has_loop": "*" in powl_string,
        "has_interleaving": "<>" in powl_string,
        "has_xor": "X(" in powl_string,
        "has_parallel": "+(" in powl_string or "PO=" in powl_string,
        "has_sequence": "->(" in powl_string,
        "has_or": "O(" in powl_string,
    }

    # Count activities (simplified - look for quoted strings)
    import re
    activities = re.findall(r"'([^']+)'", powl_string)
    structure["activities"] = activities
    structure["activity_count"] = len(activities)

    return structure


def _refine_powl(
    powl_string: str,
    issues: str,
    original_description: str
) -> str:
    """Refine a POWL model based on validation feedback.

    DEPRECATED: This function is now handled by PowlPredictor.refine().
    Kept for backward compatibility.
    """
    # Return the original POWL if cannot refine
    return powl_string


# Pattern-based POWL validator (fallback if LLM validation fails)
class PowlSyntaxValidator:
    """Validate POWL model syntax using pattern matching."""

    # Patterns for all POWL operators (simplified regex)
    VALID_PATTERNS = [
        r"^\s*\*\s*\([^)]+\)\s*$",  # *(A) or *(A, B)
        r"^\s*<>\s*\([^)]+\)\s*$",  # <>(A, B)
        r"^\s*X\s*\([^)]+\)\s*$",  # X(A, B)
        r"^\s*\+\s*\([^)]+\)\s*$",  # +(A, B)
        r"^\s*->\s*\([^)]+\)\s*$",  # ->(A, B)
        r"^\s*O\s*\([^)]+\)\s*$",  # O(A, B)
        r"^\s*PO\s*=\s*\([^)]+\)\s*$",  # PO=(nodes={...}, order={...})
    ]

    @classmethod
    def is_valid_powl(cls, powl_string: str) -> bool:
        """Check if POWL string matches any valid pattern."""
        import re
        for pattern in cls.VALID_PATTERNS:
            if re.match(pattern, powl_string, re.MULTILINE | re.DOTALL):
                return True
        return False

    @classmethod
    def detect_operators(cls, powl_string: str) -> List[str]:
        """Detect which operators are present in the POWL string."""
        operators = []
        if "*" in powl_string:
            operators.append("LOOP")
        if "<>" in powl_string:
            operators.append("INTERLEAVING")
        if "X(" in powl_string or "X (" in powl_string:
            operators.append("XOR")
        if "+(" in powl_string or "+ (" in powl_string:
            operators.append("PARALLEL")
        if "PO=" in powl_string:
            operators.append("PARTIAL_ORDER")
        if "->(" in powl_string or "-> (" in powl_string:
            operators.append("SEQUENCE")
        if "O(" in powl_string or "O (" in powl_string:
            operators.append("OR")
        return operators


__all__ = [
    "PowlPredictor",
    "POWLGenerationSignature",
    "POWLRefinementSignature",
    "generate_powl_from_text",
    "DEFAULT_MODEL",
    "DEFAULT_API_KEY",
    "DSPY_AVAILABLE",
    "PowlSyntaxValidator",
]
