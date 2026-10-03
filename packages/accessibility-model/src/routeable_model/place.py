"""Places, as seen by RouteAble and by individual providers."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PlaceCategory(StrEnum):
    MUSEUM = "museum"
    HOTEL = "hotel"
    RESTAURANT = "restaurant"
    ATTRACTION = "attraction"
    EVENT_VENUE = "event_venue"
    OTHER = "other"


class GeoLocation(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class ExternalIds(BaseModel):
    osm: str | None = None
    city_dataset: str | None = None
    website: str | None = None


class Place(BaseModel):
    """Canonical place. ``id`` is ``<provider>:<external_id>``, e.g. ``osm:node:123456``."""

    id: str
    name: str
    category: PlaceCategory = PlaceCategory.OTHER
    address: str | None = None
    location: GeoLocation
    external_ids: ExternalIds = Field(default_factory=ExternalIds)


class ExternalPlace(BaseModel):
    """A place as returned by one provider, before identity resolution."""

    external_id: str
    provider_name: str
    name: str
    category: PlaceCategory = PlaceCategory.OTHER
    address: str | None = None
    location: GeoLocation
    website_url: str | None = None
    raw: Any | None = None
