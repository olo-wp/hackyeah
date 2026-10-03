# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NATIVE_TLS=true \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp

RUN --mount=type=secret,id=routeable_ca,required=false \
    if [ -s /run/secrets/routeable_ca ]; then \
        cp /run/secrets/routeable_ca /usr/local/share/ca-certificates/routeable-ca.crt; \
        update-ca-certificates; \
    fi

RUN uv sync --no-dev

RUN useradd --create-home --uid 10001 routeable
USER routeable

EXPOSE 3001
CMD ["routeable-api"]
