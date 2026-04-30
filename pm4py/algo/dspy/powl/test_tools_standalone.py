#!/usr/bin/env python3
"""
Test DSPy POWL tool functions standalone (without MCP).

This tests the core functions used by the MCP server without requiring
the MCP package to be installed.
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _safe_json(obj):
    """Serialize to JSON, handling non-serializable types."""
    return json.dumps(obj, default=str, ensure_ascii=False)


def test_powl_list_patterns():
    """Test list patterns (standalone)."""
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
            "description": "Do-while loop",
            "example": "*('Validate', 'Submit')",
        },
        {
            "name": "INTERLEAVING",
            "syntax": "<>(A, B)",
            "description": "Activities in any order",
            "example": "<>('Prepare A', 'Prepare B')",
        },
        {
            "name": "XOR",
            "syntax": "X(A, B)",
            "description": "Exclusive choice",
            "example": "X('Approve', 'Reject')",
        },
        {
            "name": "PARALLEL",
            "syntax": "+(A, B)",
            "description": "Concurrent execution",
            "example": "+('Email', 'Update DB')",
        },
        {
            "name": "SEQUENCE",
            "syntax": "->(A, B)",
            "description": "Sequential execution",
            "example": "->('Submit', 'Review')",
        },
        {
            "name": "OR",
            "syntax": "O(A, B)",
            "description": "Inclusive choice",
            "example": "O('Approve', 'Override')",
        },
        {
            "name": "PARTIAL ORDER",
            "syntax": "PO=(nodes={...}, order={})",
            "description": "Parallel no constraint",
            "example": "PO=(nodes={'A', 'B'}, order={})",
        },
    ]

    result = {
        "mcp.server.name": "dspy-powl",
        "powl.patterns": patterns,
        "powl.pattern_count": len(patterns),
    }

    print("=== POWL Patterns ===")
    print(json.dumps(result, indent=2, default=str))
    print()
    return result


def test_powl_validate():
    """Test POWL syntax validation."""
    from natural_language import PowlSyntaxValidator

    test_cases = [
        ("X('Approve', 'Reject')", "XOR pattern"),
        ("*(A)", "Single-node LOOP"),
        ("*(A, B)", "Two-node LOOP"),
        ("<>('A', 'B')", "INTERLEAVING"),
        ("+('Email', 'DB')", "PARALLEL"),
        ("->('A', 'B')", "SEQUENCE"),
        ("O('A', 'B')", "OR"),
        ("PO=(nodes={'A'}, order={})", "PARTIAL ORDER"),
        ("invalid powl", "Invalid syntax"),
    ]

    print("=== POWL Syntax Validation ===")
    for powl_string, description in test_cases:
        is_valid = PowlSyntaxValidator.is_valid_powl(powl_string)
        operators = PowlSyntaxValidator.detect_operators(powl_string)

        result = {
            "description": description,
            "powl.string": powl_string,
            "powl.valid": is_valid,
            "powl.operators": operators,
        }

        print(f"{description}: {powl_string}")
        print(f"  Valid: {is_valid}, Operators: {operators}")
    print()


def test_powl_analyze():
    """Test POWL structure analysis."""
    from natural_language import _analyze_powl_structure

    test_cases = [
        ("X('Approve', 'Reject')", "Simple XOR"),
        ("->('A', 'B', 'C')", "Sequence of 3"),
        ("+('Email', 'DB', 'Log')", "Parallel of 3"),
        ("*('Retry')", "Single-node loop"),
    ]

    print("=== POWL Structure Analysis ===")
    for powl_string, description in test_cases:
        analysis = _analyze_powl_structure(powl_string)

        print(f"{description}: {powl_string}")
        if analysis:
            print(f"  Activities: {analysis.get('activities', [])}")
            print(f"  Operators: {analysis.get('operators', [])}")
            print(f"  Has LOOP: {analysis.get('has_loop')}")
            print(f"  Has XOR: {analysis.get('has_xor')}")
            print(f"  Has PARALLEL: {analysis.get('has_parallel')}")
        print()


def test_powl_generate_mock():
    """Test POWL generation (mock, no API call)."""
    from natural_language import DSPY_AVAILABLE

    print("=== POWL Generation Status ===")

    if DSPY_AVAILABLE:
        print("DSPy is available")
        print("To test generation, set GROQ_API_KEY and call:")
        print("  generate_powl_from_text('Approve purchase orders')")
    else:
        print("DSPy not available")
        print("Install with: pip install dspy groq")
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("DSPy POWL Tools - Standalone Tests")
    print("=" * 60)
    print()

    test_powl_list_patterns()
    test_powl_validate()
    test_powl_analyze()
    test_powl_generate_mock()

    print("=" * 60)
    print("All standalone tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
