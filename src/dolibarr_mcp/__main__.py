#!/usr/bin/env python3
"""Main entry point for the Dolibarr MCP server module."""

import sys
import os

# Add the src directory to the Python path if needed
src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from dolibarr_mcp.dolibarr_mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
