"""Applies the SQL files in ``schema/`` in lexicographic order."""

import asyncio
from importlib import resources

from .pool import create_pool


async def migrate() -> None:
    schema_dir = resources.files("routeable_database.schema")
    files = sorted(
        entry.name for entry in schema_dir.iterdir() if entry.name.endswith(".sql")
    )

    pool = create_pool()
    await pool.open(wait=True)
    try:
        async with pool.connection() as conn:
            for name in files:
                print(f"applying {name}")  # noqa: T201 - CLI output
                await conn.execute(schema_dir.joinpath(name).read_text(encoding="utf-8"))
    finally:
        await pool.close()


def main() -> None:
    asyncio.run(migrate())


if __name__ == "__main__":
    main()
