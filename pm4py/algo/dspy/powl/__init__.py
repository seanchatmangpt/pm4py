"""
DSPy-based Natural Language to POWL discovery.

This module provides natural language processing capabilities to discover
POWL (Partially Ordered Workflow Language) models from text descriptions.

Uses DSPy with Groq gpt-oss-20b model for POWL generation.

Also includes MCP (Model Context Protocol) server for LLM access.
"""

from .natural_language import generate_powl_from_text

__all__ = [
    "generate_powl_from_text",
]

# Optional MCP server export (requires mcp package)
try:
    from .mcp_server import mcp, mcp as dspy_powl_mcp
    __all__ += ["mcp", "dspy_powl_mcp"]
except ImportError:
    pass
