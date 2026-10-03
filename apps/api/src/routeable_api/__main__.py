"""`python -m routeable_api` / `routeable-api` entry point."""

import uvicorn

from .config import settings


def main() -> None:
    uvicorn.run(
        "routeable_api.main:app",
        host="0.0.0.0",  # noqa: S104 - container needs to bind all interfaces
        port=settings.api_port,
    )


if __name__ == "__main__":
    main()
