#!/usr/bin/env python3
"""
Test DSPy POWL MCP tools without MCP protocol.

This script tests the tool functions directly without running the MCP server.
Useful for testing when GROQ_API_KEY is set.
"""

import asyncio
import os
import sys


async def test_powl_health():
    """Test health check tool."""
    from mcp_server import powl_health

    result = await powl_health()
    print("=== powl_health ===")
    print(result)
    print()
    return result


async def test_powl_list_patterns():
    """Test list patterns tool."""
    from mcp_server import powl_list_patterns

    result = await powl_list_patterns()
    print("=== powl_list_patterns ===")
    print(result)
    print()
    return result


async def test_powl_validate():
    """Test POWL validation tool."""
    from mcp_server import powl_validate

    test_cases = [
        "X('Auto-approve', 'Manager approval')",  # Valid XOR
        "*(A)",  # Valid single-node LOOP
        "<>(A, B)",  # Valid INTERLEAVING
        "invalid powl",  # Invalid
    ]

    print("=== powl_validate ===")
    for powl_string in test_cases:
        result = await powl_validate(powl_string)
        print(f"Input: {powl_string}")
        print(f"Result: {result}")
        print()
    return None


async def test_powl_analyze():
    """Test POWL analysis tool."""
    from mcp_server import powl_analyze

    test_cases = [
        "X('Auto-approve', 'Manager approval')",
        "->('Submit', 'Review', 'Approve')",
        "+('Email', 'Database')",
    ]

    print("=== powl_analyze ===")
    for powl_string in test_cases:
        result = await powl_analyze(powl_string)
        print(f"Input: {powl_string}")
        print(f"Result: {result}")
        print()
    return None


async def test_powl_generate():
    """Test POWL generation tool (requires GROQ_API_KEY)."""
    from mcp_server import powl_generate, DSPY_AVAILABLE

    if not DSPY_AVAILABLE:
        print("=== powl_generate ===")
        print("DSPy not available, skipping generation test")
        print("Install with: pip install dspy groq")
        print()
        return None

    if not os.environ.get("GROQ_API_KEY"):
        print("=== powl_generate ===")
        print("GROQ_API_KEY not set, skipping generation test")
        print("Set with: export GROQ_API_KEY=your_key")
        print()
        return None

    print("=== powl_generate ===")
    print("Testing with simple process description...")
    print()

    result = await powl_generate(
        description="Approve purchase orders under $1000",
        domain="finance",
        max_refinements=1,
    )
    print(result)
    print()
    return result


async def main():
    """Run all tests."""
    print("=" * 60)
    print("DSPy POWL MCP Tools Test")
    print("=" * 60)
    print()

    # Test health
    await test_powl_health()

    # Test list patterns
    await test_powl_list_patterns()

    # Test validation
    await test_powl_validate()

    # Test analysis
    await test_powl_analyze()

    # Test generation (requires API key)
    await test_powl_generate()

    print("=" * 60)
    print("Tests complete")
    print("=" * 60)


if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(main())
