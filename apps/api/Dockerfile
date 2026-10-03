# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp

RUN uv sync --no-dev

RUN useradd --create-home --uid 10001 routeable
USER routeable

EXPOSE 3001
CMD ["routeable-api"]
