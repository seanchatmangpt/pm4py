#!/usr/bin/env python3
"""
Run DSPy POWL MCP Server.

Usage:
    python run_mcp.py

This starts the MCP server for natural language to POWL discovery.
The server communicates over stdio using JSON-RPC (MCP protocol).

Example tools:
    - powl_generate: Generate POWL from natural language
    - powl_validate: Validate POWL syntax
    - powl_analyze: Analyze POWL structure
    - powl_health: Health check
    - powl_list_patterns: List supported POWL patterns
"""

if __name__ == "__main__":
    from .mcp_server import mcp
    mcp.run()
