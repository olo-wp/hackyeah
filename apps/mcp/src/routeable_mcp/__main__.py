"""`python -m routeable_mcp` / `routeable-mcp` entry point."""

import asyncio
import os
import sys

# Shared composition root: MCP and REST must run the exact same service instance wiring.
from routeable_api.config import settings
from routeable_api.container import build_container

from .server import create_server


async def serve() -> None:
    container = await build_container(settings)
    server = create_server(container.service)
    try:
        if os.getenv("MCP_TRANSPORT", "stdio") == "http":
            await server.run_streamable_http_async(
                host=os.getenv("FASTMCP_HOST", "127.0.0.1"),
                port=int(os.getenv("FASTMCP_PORT", "3002")),
            )
        else:
            await server.run_stdio_async()
    finally:
        await container.aclose()


def main() -> None:
    asyncio.run(
        serve(), loop_factory=asyncio.SelectorEventLoop if sys.platform == "win32" else None
    )


if __name__ == "__main__":
    main()
