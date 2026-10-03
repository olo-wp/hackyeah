"""Place search, accessibility profile and evidence endpoints."""

from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel
from routeable_model import (
    AccessibilityPreferences,
    Evidence,
    FeatureKey,
    Place,
)
from routeable_engine import PlaceAccessibilityResult, PlaceSearchResult
from routeable_provider_core import SearchOptions

from ..dependencies import PlaceIdPath, ServiceDep

router = APIRouter(prefix="/api/places", tags=["places"])


class EvidenceResponse(BaseModel):
    place_id: str
    feature: FeatureKey | None = None
    evidence: list[Evidence]


@router.get("/search", response_model=PlaceSearchResult)
async def search_places(
    service: ServiceDep,
    q: Annotated[str, Query(min_length=2, max_length=120)],
    city: Annotated[str | None, Query(max_length=80)] = None,
    limit: Annotated[int, Query(ge=1, le=25)] = 10,
) -> PlaceSearchResult:
    return await service.search_places(q, SearchOptions(city=city, limit=limit))


@router.get("/{place_id}", response_model=Place)
async def get_place(service: ServiceDep, place_id: PlaceIdPath) -> Place:
    return await service.get_place(place_id)


@router.get("/{place_id}/accessibility", response_model=PlaceAccessibilityResult)
async def get_place_accessibility(
    service: ServiceDep,
    place_id: PlaceIdPath,
    preferences: Annotated[AccessibilityPreferences, Query()],
) -> PlaceAccessibilityResult:
    return await service.get_place_accessibility(place_id, preferences)


@router.get("/{place_id}/accessibility/evidence", response_model=EvidenceResponse)
async def get_accessibility_evidence(
    service: ServiceDep,
    place_id: PlaceIdPath,
    feature: FeatureKey | None = None,
) -> EvidenceResponse:
    evidence = await service.get_evidence(place_id, feature)
    return EvidenceResponse(place_id=place_id, feature=feature, evidence=evidence)
