"""OpenStreetMap provider: Nominatim for discovery, Overpass for tags."""

import json
from typing import Any

from routeable_model import (
    DataSource,
    ExternalPlace,
    GeoLocation,
    RawAccessibilityEvidence,
    SourceType,
)
from routeable_provider_core import (
    AccessibilityClassifier,
    HttpClient,
    SearchOptions,
    SourceDocument,
)

from .tags import map_osm_category

OSM_PROVIDER_NAME = "osm"

_TYPE_PREFIX = {"node": "N", "way": "W", "relation": "R"}


def _parse_external_id(external_id: str) -> tuple[str, int] | None:
    osm_type, _, raw_id = external_id.partition(":")
    if osm_type not in _TYPE_PREFIX or not raw_id.isdigit():
        return None
    return osm_type, int(raw_id)


def _to_external_place(entry: dict[str, Any]) -> ExternalPlace | None:
    osm_type = entry.get("osm_type")
    osm_id = entry.get("osm_id")
    lat, lon = entry.get("lat"), entry.get("lon")

    if osm_type not in _TYPE_PREFIX or osm_id is None or lat is None or lon is None:
        return None

    extratags: dict[str, str] = entry.get("extratags") or {}
    display_name: str = entry.get("display_name") or ""

    return ExternalPlace(
        external_id=f"{osm_type}:{osm_id}",
        provider_name=OSM_PROVIDER_NAME,
        name=entry.get("name") or display_name.split(",")[0].strip() or "Unnamed place",
        category=map_osm_category(entry.get("class"), entry.get("type")),
        address=display_name or None,
        location=GeoLocation(lat=float(lat), lng=float(lon)),
        website_url=extratags.get("website") or extratags.get("contact:website"),
        raw=entry,
    )


class OsmProvider:
    def __init__(
        self,
        nominatim_url: str = "https://nominatim.openstreetmap.org",
        overpass_url: str = "https://overpass-api.de/api/interpreter",
        user_agent: str = "RouteAble/0.1",
        timeout_s: float = 8.0,
        classifier: AccessibilityClassifier | None = None,
    ) -> None:
        self._nominatim_url = nominatim_url.rstrip("/")
        self._overpass_url = overpass_url
        self._http = HttpClient(user_agent=user_agent, timeout_s=timeout_s)
        self._classifier = classifier

    @property
    def name(self) -> str:
        return OSM_PROVIDER_NAME

    @property
    def source(self) -> DataSource:
        return DataSource(
            id=OSM_PROVIDER_NAME,
            type=SourceType.OPENSTREETMAP,
            name="OpenStreetMap",
            url="https://www.openstreetmap.org",
            license="ODbL 1.0",
        )

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]:
        options = options or SearchOptions()
        params = {
            "q": f"{query}, {options.city}" if options.city else query,
            "format": "jsonv2",
            "addressdetails": "1",
            "extratags": "1",
            "limit": str(options.limit),
        }

        payload = await self._http.get_json(f"{self._nominatim_url}/search", params=params)
        places = (_to_external_place(entry) for entry in payload)
        return [place for place in places if place is not None]

    async def get_place(self, external_id: str) -> ExternalPlace | None:
        parsed = _parse_external_id(external_id)
        if parsed is None:
            return None

        osm_type, osm_id = parsed
        params = {
            "osm_ids": f"{_TYPE_PREFIX[osm_type]}{osm_id}",
            "format": "jsonv2",
            "addressdetails": "1",
            "extratags": "1",
        }

        payload = await self._http.get_json(f"{self._nominatim_url}/lookup", params=params)
        return _to_external_place(payload[0]) if payload else None

    async def get_accessibility_data(self, place: ExternalPlace) -> list[RawAccessibilityEvidence]:
        if place.provider_name != OSM_PROVIDER_NAME:
            return []

        parsed = _parse_external_id(place.external_id)
        if parsed is None:
            return []

        osm_type, osm_id = parsed
        payload = await self._http.post_form_json(
            self._overpass_url,
            {"data": f"[out:json][timeout:25];{osm_type}({osm_id});out tags;"},
        )

        elements = payload.get("elements") or []
        tags = elements[0].get("tags") if elements else None
        if not tags:
            return []

        if self._classifier is None:
            raise RuntimeError("An AI accessibility classifier is required for OSM data")
        return await self._classifier.classify(
            place,
            [
                SourceDocument(
                    url=f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
                    text=json.dumps(tags, ensure_ascii=False),
                )
            ],
        )

    async def aclose(self) -> None:
        await self._http.aclose()
