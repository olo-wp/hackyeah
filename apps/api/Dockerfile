# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /bin/uv

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NATIVE_TLS=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

ARG CACHE_BUSTER=none
RUN --mount=type=secret,id=routeable_ca,target=/tmp/routeable-ca.crt,required=false \
        if [ -s /tmp/routeable-ca.crt ]; then \
            cp /tmp/routeable-ca.crt /usr/local/share/ca-certificates/routeable-ca.crt && \
            update-ca-certificates; \
        fi

COPY pyproject.toml ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY apps/mcp ./apps/mcp

RUN uv sync --no-dev

COPY --chmod=755 apps/api/entrypoint.sh /usr/local/bin/routeable-api-entrypoint

RUN useradd --create-home --uid 10001 routeable
USER routeable

EXPOSE 3001
ENTRYPOINT ["routeable-api-entrypoint"]
CMD ["routeable-api"]
