"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routeable_engine import PlaceNotFoundError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .config import Settings, settings
from .container import build_container
from .routers import places, reports

logging.basicConfig(level=logging.INFO)


def create_app(app_settings: Settings | None = None) -> FastAPI:
    app_settings = app_settings or settings
    limiter = Limiter(key_func=get_remote_address, default_limits=[app_settings.rate_limit])

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.container = await build_container(app_settings)
        try:
            yield
        finally:
            await app.state.container.aclose()

    app = FastAPI(
        title="RouteAble API",
        version="0.1.0",
        summary="Accessibility facts with sources, confidence and conflicts — never a verdict.",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.exception_handler(PlaceNotFoundError)
    async def place_not_found(_request: Request, error: PlaceNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404, content={"error": "place_not_found", "message": str(error)}
        )

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "routeable-api"}

    app.include_router(places.router)
    app.include_router(reports.router)

    return app


app = create_app()
