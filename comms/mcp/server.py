"""MCP server for the Comms pipeline."""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent

from .tools import TOOL_DEFINITIONS, call_tool

logger = logging.getLogger(__name__)


def create_server() -> Server:
    server = Server("comms")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=defn["name"],
                description=defn["description"],
                inputSchema=defn["input_schema"],
            )
            for defn in TOOL_DEFINITIONS
        ]

    @server.call_tool()
    async def handle_tool_call(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        logger.info(f"Tool call: {name} with args: {arguments}")
        result = await call_tool(name, arguments)
        return [TextContent(type="text", text=result)]

    return server
