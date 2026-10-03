"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, Path, Request
from routeable_engine import AccessibilityService

PLACE_ID_PATTERN = r"^[a-z0-9_-]+:[A-Za-z0-9:_.-]+$"


def get_service(request: Request) -> AccessibilityService:
    service: AccessibilityService = request.app.state.container.service
    return service


ServiceDep = Annotated[AccessibilityService, Depends(get_service)]

PlaceIdPath = Annotated[
    str,
    Path(
        min_length=3,
        max_length=120,
        pattern=PLACE_ID_PATTERN,
        description="RouteAble place id, e.g. `osm:node:123456`",
    ),
]
