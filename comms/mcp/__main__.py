"""
Entry point for running the MCP server.

Run with: python -m comms.mcp
"""

import asyncio
import logging

from dotenv import load_dotenv
from mcp.server.stdio import stdio_server

load_dotenv()

from .server import create_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting Comms MCP server...")
    server = create_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
