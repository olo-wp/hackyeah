"""Connection pool helpers."""

import os

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool


def resolve_database_url(database_url: str | None = None) -> str:
    url = database_url or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set")
    return url


def create_pool(database_url: str | None = None, max_size: int = 10) -> AsyncConnectionPool:
    """Pool is opened lazily by the caller (FastAPI lifespan) to keep startup explicit."""
    return AsyncConnectionPool(
        conninfo=resolve_database_url(database_url),
        max_size=max_size,
        open=False,
        kwargs={"row_factory": dict_row},
    )
