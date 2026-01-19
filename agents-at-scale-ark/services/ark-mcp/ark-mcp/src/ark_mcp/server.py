"""Ark MCP Server - Provides tools for interacting with Ark resources."""

import logging
from fastmcp import FastMCP
from .resources import register_resources
from .tools import register_tools

logger = logging.getLogger(__name__)

# Create the MCP server
mcp = FastMCP("Ark 🏗️")

# Register resources and tools
register_resources(mcp)
register_tools(mcp)


def create_app():
    """Create the MCP server application."""
    return mcp