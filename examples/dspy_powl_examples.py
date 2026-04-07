"""
DSPy Examples Library for POWL (Partially Ordered Workflow Language)

This library demonstrates all major DSPy 3.x patterns applied to process mining:
- Signatures: typed input/output contracts
- Modules: reusable components with internal prompting
- ChainOfThought: multi-step reasoning
- MultiChainComparison: evaluating multiple outputs
- Assertions: computational constraints
- Optimization: prompt and weight optimization
"""

import dspy
from typing import List, Dict, Any
import pm4py


# ============================================================================
# PATTERN 1: Basic Signature & Module
# ============================================================================

class BasicExplainPOWL(dspy.Signature):
    """Explain what a POWL process model does."""
    powl_model: str = dspy.InputField(desc="POWL model as text")
    explanation: str = dspy.OutputField(desc="What the process does")


class POWLExplainerBasic(dspy.Module):
    """Simplest possible explainer - just uses Predict (no reasoning)."""
    def __init__(self):
        super().__init__()
        self.explain = dspy.Predict(BasicExplainPOWL)

    def forward(self, powl_model: str):
        return self.explain(powl_model=powl_model)


# Example: Basic explanation
def example_1_basic_signature_module():
    """PATTERN 1: Basic Signature & Module"""
    print("\n=== PATTERN 1: Basic Signature & Module ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    powl_text = pm4py.llm.abstract_powl(powl, response_header=False)

    explainer = POWLExplainerBasic()
    result = explainer(powl_model=powl_text)
    print(f"Explanation: {result.explanation[:200]}...")


# ============================================================================
# PATTERN 2: ChainOfThought (Multi-step Reasoning)
# ============================================================================

class ReasonedPOWLExplanation(dspy.Signature):
    """Explain a POWL model with step-by-step reasoning."""
    powl_model: str = dspy.InputField(desc="POWL model as text")
    reasoning: str = dspy.OutputField(desc="Step-by-step analysis")
    explanation: str = dspy.OutputField(desc="Final explanation")


class POWLExplainerChainOfThought(dspy.Module):
    """Explainer that reasons through the model step-by-step."""
    def __init__(self):
        super().__init__()
        self.explain = dspy.ChainOfThought(ReasonedPOWLExplanation)

    def forward(self, powl_model: str):
        return self.explain(powl_model=powl_model)


def example_2_chain_of_thought():
    """PATTERN 2: ChainOfThought for reasoning"""
    print("\n=== PATTERN 2: ChainOfThought (Multi-step Reasoning) ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    powl_text = pm4py.llm.abstract_powl(powl, response_header=False)

    explainer = POWLExplainerChainOfThought()
    result = explainer(powl_model=powl_text)
    print(f"Reasoning:\n{result.reasoning}\n")
    print(f"Explanation:\n{result.explanation[:200]}...")


# ============================================================================
# PATTERN 3: Multiple Outputs & Aggregation
# ============================================================================

class POWLQualityAssessment(dspy.Signature):
    """Assess the quality of a POWL model."""
    powl_model: str = dspy.InputField(desc="POWL model")
    assessment: str = dspy.OutputField(desc="Quality assessment")
    score: int = dspy.OutputField(desc="Quality score 1-10")


class POWLQualityEvaluator(dspy.Module):
    """Evaluate model quality from multiple perspectives."""
    def __init__(self):
        super().__init__()
        self.clarity = dspy.ChainOfThought(POWLQualityAssessment)

    def forward(self, powl_model: str):
        # Generate 3 independent assessments
        assessments = []
        for i in range(3):
            result = self.clarity(powl_model=powl_model)
            assessments.append(result)

        avg_score = sum(a.score for a in assessments) / len(assessments)
        return {
            "assessments": [a.assessment for a in assessments],
            "scores": [a.score for a in assessments],
            "average_score": avg_score
        }


def example_3_multiple_outputs():
    """PATTERN 3: Multiple outputs and aggregation"""
    print("\n=== PATTERN 3: Multiple Outputs & Aggregation ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    powl_text = pm4py.llm.abstract_powl(powl, response_header=False)

    evaluator = POWLQualityEvaluator()
    result = evaluator(powl_model=powl_text)
    print(f"Assessments: {result['assessments']}")
    print(f"Scores: {result['scores']}")
    print(f"Average Quality Score: {result['average_score']:.1f}/10")


# ============================================================================
# PATTERN 4: Modular Pipeline (Chaining Modules)
# ============================================================================

class ExtractActivities(dspy.Signature):
    """Extract activities from POWL model."""
    powl_model: str = dspy.InputField()
    activities: List[str] = dspy.OutputField(desc="List of activity names")


class AnalyzeActivityRoles(dspy.Signature):
    """Analyze roles of extracted activities."""
    activities: List[str] = dspy.InputField()
    roles: Dict[str, str] = dspy.OutputField(desc="Activity -> Role mapping")


class POWLActivityPipeline(dspy.Module):
    """Pipeline: Extract activities -> Analyze roles"""
    def __init__(self):
        super().__init__()
        self.extractor = dspy.ChainOfThought(ExtractActivities)
        self.analyzer = dspy.ChainOfThought(AnalyzeActivityRoles)

    def forward(self, powl_model: str):
        # Step 1: Extract
        extraction = self.extractor(powl_model=powl_model)

        # Step 2: Analyze (using output from step 1)
        analysis = self.analyzer(activities=extraction.activities)

        return {
            "activities": extraction.activities,
            "roles": analysis.roles
        }


def example_4_modular_pipeline():
    """PATTERN 4: Modular pipeline (chaining modules)"""
    print("\n=== PATTERN 4: Modular Pipeline ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    powl_text = pm4py.llm.abstract_powl(powl, response_header=False)

    pipeline = POWLActivityPipeline()
    result = pipeline(powl_model=powl_text)
    print(f"Activities: {result['activities']}")
    print(f"Roles: {result['roles']}")


# ============================================================================
# PATTERN 5: Assertions (Constraints)
# ============================================================================

class ValidPOWLGeneration(dspy.Signature):
    """Generate a valid POWL model string."""
    description: str = dspy.InputField(desc="Process description")
    powl_string: str = dspy.OutputField(desc="POWL model")


class ValidatedPOWLDiscoverer(dspy.Module):
    """Generate POWL with assertion validation."""
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought(ValidPOWLGeneration)

    def forward(self, description: str):
        result = self.generator(description=description)

        # Assertion: Generated string must be parseable
        try:
            powl_model = pm4py.objects.powl.parser.parse_powl_model_string(result.powl_string)
            return result
        except Exception as e:
            # If assertion fails, generate again with correction prompt
            correction = self.generator(description=f"{description}\n\nMake sure format is valid POWL like: PO=(nodes={{A, B}}, order={{A-->B}})")
            return correction


def example_5_assertions():
    """PATTERN 5: Assertions for constraint validation"""
    print("\n=== PATTERN 5: Assertions (Constraints) ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    desc = "A simple process: submit request, then approval, then payment"

    discoverer = ValidatedPOWLDiscoverer()
    result = discoverer(description=desc)
    print(f"Generated POWL:\n{result.powl_string}")

    # Validate it works
    try:
        powl = pm4py.objects.powl.parser.parse_powl_model_string(result.powl_string)
        print("✓ POWL is valid and parseable")
    except:
        print("✗ POWL is invalid")


# ============================================================================
# PATTERN 6: Context Management
# ============================================================================

class ImprovedExplanation(dspy.Signature):
    """Explain POWL with context."""
    powl_model: str = dspy.InputField()
    business_domain: str = dspy.InputField(desc="e.g., 'insurance claims', 'loan approval'")
    explanation: str = dspy.OutputField()


class ContextAwarePOWLExplainer(dspy.Module):
    """Explainer that uses context to improve explanations."""
    def __init__(self, business_domain: str):
        super().__init__()
        self.domain = business_domain
        self.explain = dspy.ChainOfThought(ImprovedExplanation)

    def forward(self, powl_model: str):
        return self.explain(
            powl_model=powl_model,
            business_domain=self.domain
        )


def example_6_context_management():
    """PATTERN 6: Context management for customization"""
    print("\n=== PATTERN 6: Context Management ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    powl_text = pm4py.llm.abstract_powl(powl, response_header=False)

    # Different explainers for different domains
    insurance_explainer = ContextAwarePOWLExplainer("insurance claims")
    finance_explainer = ContextAwarePOWLExplainer("loan approval")

    insurance_result = insurance_explainer(powl_model=powl_text)
    finance_result = finance_explainer(powl_model=powl_text)

    print(f"Insurance perspective: {insurance_result.explanation[:150]}...\n")
    print(f"Finance perspective: {finance_result.explanation[:150]}...")


# ============================================================================
# PATTERN 7: Type Checking & Validation
# ============================================================================

class StructuredComparison(dspy.Signature):
    """Compare POWL models with structured output."""
    powl_1: str = dspy.InputField(desc="First model")
    powl_2: str = dspy.InputField(desc="Second model")
    main_differences: List[str] = dspy.OutputField(desc="List of key differences")
    structural_similarity: float = dspy.OutputField(desc="0.0-1.0 similarity score")
    recommendations: List[str] = dspy.OutputField(desc="Improvement recommendations")


class TypedPOWLComparator(dspy.Module):
    """Comparator that enforces structured output types."""
    def __init__(self):
        super().__init__()
        self.compare = dspy.ChainOfThought(StructuredComparison)

    def forward(self, powl_1: str, powl_2: str):
        result = self.compare(powl_1=powl_1, powl_2=powl_2)

        # Type validation
        assert isinstance(result.main_differences, list)
        assert isinstance(result.structural_similarity, float)
        assert 0.0 <= result.structural_similarity <= 1.0
        assert isinstance(result.recommendations, list)

        return result


def example_7_type_checking():
    """PATTERN 7: Type checking and validation"""
    print("\n=== PATTERN 7: Type Checking & Validation ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl_1 = pm4py.discover_powl(log)
    powl_2 = pm4py.discover_powl(log)

    text_1 = pm4py.llm.abstract_powl(powl_1, response_header=False)
    text_2 = pm4py.llm.abstract_powl(powl_2, response_header=False)

    comparator = TypedPOWLComparator()
    result = comparator(powl_1=text_1, powl_2=text_2)

    print(f"Differences: {result.main_differences}")
    print(f"Similarity: {result.structural_similarity:.2f}")
    print(f"Recommendations: {result.recommendations}")


# ============================================================================
# PATTERN 8: Error Handling & Retry
# ============================================================================

class RobustPOWLGeneration(dspy.Signature):
    """Generate valid POWL with error handling."""
    description: str = dspy.InputField()
    powl_string: str = dspy.OutputField()


class RobustDiscoverer(dspy.Module):
    """Discoverer with automatic retry on validation failure."""
    def __init__(self, max_retries=3):
        super().__init__()
        self.generator = dspy.ChainOfThought(RobustPOWLGeneration)
        self.max_retries = max_retries

    def forward(self, description: str):
        for attempt in range(self.max_retries):
            try:
                result = self.generator(description=description)
                # Try to parse
                pm4py.objects.powl.parser.parse_powl_model_string(result.powl_string)
                return result
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                # Retry with hint
                description = f"{description}\n\nPrevious attempt failed: {str(e)[:100]}. Ensure valid POWL syntax."

        return result


def example_8_error_handling():
    """PATTERN 8: Error handling and retry"""
    print("\n=== PATTERN 8: Error Handling & Retry ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    desc = "Process: A, then B or C, then D"

    discoverer = RobustDiscoverer(max_retries=3)
    try:
        result = discoverer(description=desc)
        print(f"✓ Successfully generated: {result.powl_string[:100]}...")
    except Exception as e:
        print(f"✗ Failed after retries: {e}")


# ============================================================================
# PATTERN 9: Batch Processing
# ============================================================================

def example_9_batch_processing():
    """PATTERN 9: Batch processing multiple models"""
    print("\n=== PATTERN 9: Batch Processing ===")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    # Load multiple logs
    import os
    log_dir = "input_data"
    log_files = [f for f in os.listdir(log_dir) if f.endswith(".xes")][:3]

    explainer = POWLExplainerChainOfThought()
    results = {}

    for log_file in log_files:
        try:
            log = pm4py.read_xes(os.path.join(log_dir, log_file), return_legacy_log_object=True)
            powl = pm4py.discover_powl(log)
            text = pm4py.llm.abstract_powl(powl, response_header=False)

            result = explainer(powl_model=text)
            results[log_file] = result.explanation[:100] + "..."
        except:
            continue

    for log_file, explanation in results.items():
        print(f"{log_file}: {explanation}")


# ============================================================================
# PATTERN 10: Optimization (Advanced)
# ============================================================================

class OptimizableExplanation(dspy.Signature):
    """Explain POWL - signature optimizable for quality."""
    powl_model: str = dspy.InputField()
    explanation: str = dspy.OutputField()


class OptimizablePOWLExplainer(dspy.Module):
    """Explainer that can be optimized with BootstrapFewShot."""
    def __init__(self):
        super().__init__()
        self.explain = dspy.ChainOfThought(OptimizableExplanation)

    def forward(self, powl_model: str):
        return self.explain(powl_model=powl_model)


def example_10_optimization():
    """PATTERN 10: Optimization with BootstrapFewShot (Advanced)"""
    print("\n=== PATTERN 10: Optimization (BootstrapFewShot) ===")
    print("Note: Optimization requires training examples. This shows the structure.")

    dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

    # Create some example POWL models for training
    log = pm4py.read_xes("input_data/running-example.xes", return_legacy_log_object=True)
    powl = pm4py.discover_powl(log)
    powl_text = pm4py.llm.abstract_powl(powl, response_header=False)

    # In a real scenario, you would:
    # 1. Create training examples with good explanations
    # 2. Use BootstrapFewShot to optimize
    # 3. Evaluate on test set

    explainer = OptimizablePOWLExplainer()
    result = explainer(powl_model=powl_text)
    print(f"Explanation: {result.explanation[:150]}...")
    print("\nIn production, use BootstrapFewShot to optimize prompts based on your examples.")


# ============================================================================
# MAIN: Run all examples
# ============================================================================

if __name__ == "__main__":
    import sys

    examples = [
        ("1", "Basic Signature & Module", example_1_basic_signature_module),
        ("2", "ChainOfThought", example_2_chain_of_thought),
        ("3", "Multiple Outputs", example_3_multiple_outputs),
        ("4", "Modular Pipeline", example_4_modular_pipeline),
        ("5", "Assertions", example_5_assertions),
        ("6", "Context Management", example_6_context_management),
        ("7", "Type Checking", example_7_type_checking),
        ("8", "Error Handling", example_8_error_handling),
        ("9", "Batch Processing", example_9_batch_processing),
        ("10", "Optimization", example_10_optimization),
    ]

    print("""
    DSPy Examples for POWL - All Major Patterns
    ============================================

    Available examples:
    """)

    for num, name, _ in examples:
        print(f"  {num}. {name}")

    print("\nUsage:")
    print("  python dspy_powl_examples.py              # Run all")
    print("  python dspy_powl_examples.py 1            # Run example 1")
    print("  python dspy_powl_examples.py 1 2 3        # Run examples 1, 2, 3")

    if len(sys.argv) == 1:
        # Run all
        for _, _, example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Run selected
        for arg in sys.argv[1:]:
            for num, name, example_func in examples:
                if num == arg:
                    print(f"\n{'='*60}")
                    try:
                        example_func()
                    except Exception as e:
                        print(f"Error in {name}: {e}")
                    break
