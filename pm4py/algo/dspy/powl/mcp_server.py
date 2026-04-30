"""
DSPy NL→POWL MCP Server — Exposes natural language to POWL discovery via MCP.

This server provides Model Context Protocol tools for discovering POWL models
from natural language descriptions using DSPy with Groq gpt-oss-20b.

Semantic Conventions (weaver/OTel):
- mcp.server.name: "dspy-powl"
- mcp.tool.name: Tool names (powl_generate, powl_validate, powl_analyze)
- powl.model.slug: URL-safe slug for the model
- powl.model.fitness: Conformance fitness score
- powl.iteration.count: Number of LLM iterations
- powl.model.operator_types: POWL operators present
- powl.discovery.variant: Discovery algorithm
"""

import importlib.util
import json
import os
import sys
from typing import Any, Dict, Optional

# Add parent directory to path for imports
_DSPY_DIR = os.path.dirname(os.path.abspath(__file__))
if _DSPY_DIR not in sys.path:
    sys.path.insert(0, _DSPY_DIR)

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "FastMCP not installed. Install with: pip install mcp"
    )

# Import natural_language module
try:
    from natural_language import (
        generate_powl_from_text,
        PowlSyntaxValidator,
        DEFAULT_MODEL,
        DSPY_AVAILABLE,
    )
except ImportError:
    # Try relative import
    import importlib
    nl = importlib.import_module(".natural_language", package="pm4py.algo.dspy.powl")
    generate_powl_from_text = nl.generate_powl_from_text
    PowlSyntaxValidator = nl.PowlSyntaxValidator
    DEFAULT_MODEL = nl.DEFAULT_MODEL
    DSPY_AVAILABLE = nl.DSPY_AVAILABLE


mcp = FastMCP("dspy-powl")


def _safe_json(obj: Any, default=str) -> str:
    """Serialize to JSON, handling non-serializable types."""
    return json.dumps(obj, default=default, ensure_ascii=False)


def _format_powl_result(result: Dict[str, Any], description: str) -> Dict[str, Any]:
    """Format POWL generation result with semantic conventions.

    Args:
        result: Result from generate_powl_from_text()
        description: Original process description

    Returns:
        Formatted result with weaver/OTel semantic conventions
    """
    formatted = {
        "mcp.server.name": "dspy-powl",
        "mcp.tool.name": "powl_generate",
        "mcp.tool.success": result.get("verdict", False),
        "powl.model.slug": _slugify(description),
        "powl.iteration.count": result.get("refinements", 0),
        "powl.discovery.variant": "dspy-groq",
    }

    if result.get("powl"):
        formatted["powl.model"] = result["powl"]
        formatted["powl.model.string"] = str(result["powl"])

    if result.get("analysis"):
        analysis = result["analysis"]
        if analysis.get("operator_types"):
            formatted["powl.model.operator_types"] = analysis["operator_types"]
        if analysis.get("activity_count"):
            formatted["powl.model.activity_count"] = analysis["activity_count"]

    if result.get("verdict"):
        formatted["powl.threshold_met"] = True
        # Default fitness when verdict is True (no actual event log for DSPy)
        formatted["powl.model.fitness"] = 1.0
    else:
        formatted["powl.threshold_met"] = False
        formatted["powl.model.fitness"] = 0.0
        if result.get("feedback"):
            formatted["powl.error_category"] = "semantic"
            formatted["powl.error_message"] = result["feedback"]

    if result.get("reasoning"):
        formatted["powl.reasoning"] = result["reasoning"]

    return formatted


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    # Remove special chars, replace spaces with hyphens, lowercase
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:50]  # Limit length


# ---------------------------------------------------------------------------
# 1. Health check
# ---------------------------------------------------------------------------

@mcp.tool()
async def powl_health() -> str:
    """Health check for DSPy POWL MCP server. Returns DSPy availability and default model."""
    try:
        result = {
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_health",
            "mcp.tool.success": True,
            "dspy.available": DSPY_AVAILABLE,
            "default.model": DEFAULT_MODEL if DSPY_AVAILABLE else None,
            "status": "ok" if DSPY_AVAILABLE else "dspy_unavailable",
        }
        return _safe_json(result)
    except Exception as e:
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_health",
            "mcp.tool.success": False,
            "error": str(e),
        })


# ---------------------------------------------------------------------------
# 2. Generate POWL from natural language
# ---------------------------------------------------------------------------

@mcp.tool()
async def powl_generate(
    description: str,
    domain: Optional[str] = None,
    max_refinements: int = 2,
    use_demos: bool = True,
    model: str = DEFAULT_MODEL,
) -> str:
    """Generate POWL model from natural language description using DSPy with Groq.

    Args:
        description: Natural language description of the business process
        domain: Optional domain context (e.g., 'healthcare', 'finance')
        max_refinements: Maximum number of judge-and-refine iterations (default: 2)
        use_demos: Whether to use few-shot examples (default: True)
        model: Groq model identifier (default: groq/openai/gpt-oss-20b)

    Returns:
        POWL model with semantic conventions (powl.model.slug, powl.iteration.count, etc.)
    """
    try:
        if not DSPY_AVAILABLE:
            return _safe_json({
                "mcp.server.name": "dspy-powl",
                "mcp.tool.name": "powl_generate",
                "mcp.tool.success": False,
                "error": "DSPy not available. Install with: pip install dspy groq",
                "error.type": "ImportError",
            })

        result = generate_powl_from_text(
            process_description=description,
            model=model,
            max_refinements=max_refinements,
            use_demos=use_demos,
            domain=domain,
        )

        formatted = _format_powl_result(result, description)
        formatted["mcp.tool.args"] = _safe_json({
            "description": description[:100],  # Truncate for logging
            "domain": domain,
            "max_refinements": max_refinements,
            "use_demos": use_demos,
        })

        return _safe_json(formatted)
    except Exception as e:
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_generate",
            "mcp.tool.success": False,
            "error": str(e),
            "error.type": type(e).__name__,
        })


# ---------------------------------------------------------------------------
# 3. Validate POWL syntax
# ---------------------------------------------------------------------------

@mcp.tool()
async def powl_validate(powl_string: str) -> str:
    """Validate POWL model syntax using pattern matching.

    Args:
        powl_string: POWL model string to validate

    Returns:
        Validation result with detected operators and syntax check
    """
    try:
        is_valid = PowlSyntaxValidator.is_valid_powl(powl_string)
        operators = PowlSyntaxValidator.detect_operators(powl_string)

        result = {
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_validate",
            "mcp.tool.success": True,
            "powl.string": powl_string,
            "powl.valid": is_valid,
            "powl.operators": operators,
            "powl.operator_count": len(operators),
        }

        if not is_valid:
            result["powl.error_category"] = "schema"
            result["powl.error_message"] = "POWL syntax does not match any valid pattern"

        return _safe_json(result)
    except Exception as e:
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_validate",
            "mcp.tool.success": False,
            "error": str(e),
            "error.type": type(e).__name__,
        })


# ---------------------------------------------------------------------------
# 4. Analyze POWL structure
# ---------------------------------------------------------------------------

@mcp.tool()
async def powl_analyze(powl_string: str) -> str:
    """Analyze POWL model structure and extract metrics.

    Args:
        powl_string: POWL model string to analyze

    Returns:
        Structural analysis with operator types, activities, and complexity metrics
    """
    try:
        from natural_language import _analyze_powl_structure

        analysis = _analyze_powl_structure(powl_string)

        result = {
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_analyze",
            "mcp.tool.success": True,
            "powl.string": powl_string,
        }

        if analysis:
            result["powl.model.operator_types"] = analysis.get("operators", [])
            result["powl.model.activities"] = analysis.get("activities", [])
            result["powl.model.activity_count"] = analysis.get("activity_count", 0)

            # Complexity metrics
            operator_count = len(analysis.get("operators", []))
            activity_count = analysis.get("activity_count", 0)
            result["powl.model.complexity"] = {
                "operator_count": operator_count,
                "activity_count": activity_count,
                "total_nodes": operator_count + activity_count,
            }

            # Pattern detection
            patterns = []
            if analysis.get("has_loop"):
                patterns.append("loop")
            if analysis.get("has_interleaving"):
                patterns.append("interleaving")
            if analysis.get("has_xor"):
                patterns.append("xor")
            if analysis.get("has_parallel"):
                patterns.append("parallel")
            if analysis.get("has_sequence"):
                patterns.append("sequence")
            if analysis.get("has_or"):
                patterns.append("or")
            result["powl.model.patterns"] = patterns

        return _safe_json(result)
    except Exception as e:
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_analyze",
            "mcp.tool.success": False,
            "error": str(e),
            "error.type": type(e).__name__,
        })


# ---------------------------------------------------------------------------
# 5. Batch generate with retry
# ---------------------------------------------------------------------------

@mcp.tool()
async def powl_generate_with_retry(
    description: str,
    domain: Optional[str] = None,
    max_attempts: int = 3,
    max_refinements: int = 2,
    model: str = DEFAULT_MODEL,
) -> str:
    """Generate POWL with automatic retry on failure.

    Attempts generation up to max_attempts times. Returns the first successful
    result or the last error if all attempts fail.

    Args:
        description: Natural language description of the business process
        domain: Optional domain context
        max_attempts: Maximum number of generation attempts (default: 3)
        max_refinements: Refinements per attempt (default: 2)
        model: Groq model identifier

    Returns:
        POWL model with attempt count and success status
    """
    try:
        if not DSPY_AVAILABLE:
            return _safe_json({
                "mcp.server.name": "dspy-powl",
                "mcp.tool.name": "powl_generate_with_retry",
                "mcp.tool.success": False,
                "error": "DSPy not available",
                "error.type": "ImportError",
            })

        last_error = None
        for attempt in range(max_attempts):
            try:
                result = generate_powl_from_text(
                    process_description=description,
                    model=model,
                    max_refinements=max_refinements,
                    use_demos=True,
                    domain=domain,
                )

                if result.get("verdict"):
                    formatted = _format_powl_result(result, description)
                    formatted["powl.generation.attempts"] = attempt + 1
                    formatted["powl.generation.max_attempts"] = max_attempts
                    formatted["mcp.tool.args"] = _safe_json({
                        "description": description[:100],
                        "domain": domain,
                        "max_attempts": max_attempts,
                    })
                    return _safe_json(formatted)

                last_error = result.get("reasoning", "Unknown error")

            except Exception as e:
                last_error = str(e)

        # All attempts failed
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_generate_with_retry",
            "mcp.tool.success": False,
            "powl.threshold_met": False,
            "powl.generation.attempts": max_attempts,
            "powl.generation.max_attempts": max_attempts,
            "error": "All generation attempts failed",
            "error.type": "GenerationError",
            "last_error": last_error,
        })
    except Exception as e:
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_generate_with_retry",
            "mcp.tool.success": False,
            "error": str(e),
            "error.type": type(e).__name__,
        })


# ---------------------------------------------------------------------------
# 6. List supported POWL patterns
# ---------------------------------------------------------------------------

@mcp.tool()
async def powl_list_patterns() -> str:
    """List all supported POWL patterns with examples.

    Returns:
        List of POWL operators with syntax examples and descriptions
    """
    try:
        patterns = [
            {
                "name": "LOOP (single node)",
                "syntax": "*(A)",
                "description": "Repeat the same activity",
                "example": "*('Retry approval')",
            },
            {
                "name": "LOOP (two node)",
                "syntax": "*(A, B)",
                "description": "Do-while loop: execute B, then repeat A if condition fails",
                "example": "*('Validate fields', 'Submit data')",
            },
            {
                "name": "INTERLEAVING",
                "syntax": "<>(A, B)",
                "description": "Activities can execute in any order",
                "example": "<>('Prepare A', 'Prepare B')",
            },
            {
                "name": "XOR (Exclusive Choice)",
                "syntax": "X(A, B)",
                "description": "Either A or B, not both",
                "example": "X('Auto-approve', 'Manager approval')",
            },
            {
                "name": "PARALLEL",
                "syntax": "+(A, B)",
                "description": "Concurrent execution",
                "example": "+('Send email', 'Update database')",
            },
            {
                "name": "SEQUENCE",
                "syntax": "->(A, B)",
                "description": "Sequential execution (A then B)",
                "example": "->('Submit expense', 'Manager review')",
            },
            {
                "name": "OR (Inclusive Choice)",
                "syntax": "O(A, B)",
                "description": "Either A, B, or both",
                "example": "O('Auto-approve', 'Manager override')",
            },
            {
                "name": "PARTIAL ORDER",
                "syntax": "PO=(nodes={...}, order={})",
                "description": "Parallel with no ordering constraint",
                "example": "PO=(nodes={'Payment', 'Email'}, order={})",
            },
        ]

        result = {
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_list_patterns",
            "mcp.tool.success": True,
            "powl.patterns": patterns,
            "powl.pattern_count": len(patterns),
        }

        return _safe_json(result)
    except Exception as e:
        return _safe_json({
            "mcp.server.name": "dspy-powl",
            "mcp.tool.name": "powl_list_patterns",
            "mcp.tool.success": False,
            "error": str(e),
            "error.type": type(e).__name__,
        })


if __name__ == "__main__":
    mcp.run()
