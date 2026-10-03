"""`python -m routeable_api` / `routeable-api` entry point."""

import asyncio
import sys

import uvicorn

from .config import settings


def main() -> None:
    uvicorn.run(
        "routeable_api.main:app",
        host="0.0.0.0",  # noqa: S104 - container needs to bind all interfaces
        port=settings.api_port,
        loop=asyncio.SelectorEventLoop if sys.platform == "win32" else "auto",
    )


if __name__ == "__main__":
    main()
