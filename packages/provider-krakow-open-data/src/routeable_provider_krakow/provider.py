"""Second data source for the MVP.

Today it reads a curated snapshot; replacing ``_load_dataset`` with an HTTP call to
Otwarte Dane / MSIP is the only change needed to go live.
"""

import json
from datetime import datetime
from importlib import resources
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from routeable_model import (
    DataSource,
    ExternalPlace,
    GeoLocation,
    PlaceCategory,
    RawAccessibilityEvidence,
    SourceType,
    VerificationStatus,
    is_feature_key,
)
from routeable_provider_core import SearchOptions, distance_meters, normalize_name

KRAKOW_PROVIDER_NAME = "krakow"
MAX_MATCH_DISTANCE_M = 150.0


class DatasetEntry(BaseModel):
    external_id: str
    name: str
    category: PlaceCategory = PlaceCategory.OTHER
    address: str | None = None
    location: GeoLocation
    website_url: str | None = None
    osm_external_id: str | None = None
    observed_at: datetime | None = None
    features: dict[str, Any] = Field(default_factory=dict)


class Dataset(BaseModel):
    dataset_name: str
    retrieved_at: datetime
    entries: list[DatasetEntry] = Field(default_factory=list)


def _load_dataset(path: Path | None) -> Dataset:
    if path is None:
        raw = (
            resources.files("routeable_provider_krakow.data")
            .joinpath("demo_places.json")
            .read_text(encoding="utf-8")
        )
    else:
        raw = path.read_text(encoding="utf-8")
    return Dataset.model_validate(json.loads(raw))


def _to_external_place(entry: DatasetEntry) -> ExternalPlace:
    return ExternalPlace(
        external_id=entry.external_id,
        provider_name=KRAKOW_PROVIDER_NAME,
        name=entry.name,
        category=entry.category,
        address=entry.address,
        location=entry.location,
        website_url=entry.website_url,
        raw=entry.model_dump(mode="json"),
    )


class KrakowOpenDataProvider:
    def __init__(
        self, dataset_path: Path | None = None, is_official_dataset: bool = False
    ) -> None:
        self._dataset = _load_dataset(dataset_path)
        self._source_type = (
            SourceType.CITY_OPEN_DATA if is_official_dataset else SourceType.DEMO_DATA
        )

    @property
    def name(self) -> str:
        return KRAKOW_PROVIDER_NAME

    @property
    def source(self) -> DataSource:
        return DataSource(
            id=KRAKOW_PROVIDER_NAME,
            type=self._source_type,
            name=self._dataset.dataset_name,
            url="https://otwartedane.krakow.pl",
            license="CC BY 4.0",
        )

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]:
        options = options or SearchOptions()
        needle = normalize_name(query)
        matches = [
            entry for entry in self._dataset.entries if needle in normalize_name(entry.name)
        ]
        return [_to_external_place(entry) for entry in matches[: options.limit]]

    async def get_place(self, external_id: str) -> ExternalPlace | None:
        entry = next(
            (item for item in self._dataset.entries if item.external_id == external_id), None
        )
        return _to_external_place(entry) if entry else None

    async def get_accessibility_data(
        self, place: ExternalPlace
    ) -> list[RawAccessibilityEvidence]:
        entry = self._match(place)
        if entry is None:
            return []

        return [
            RawAccessibilityEvidence(
                feature_key=feature_key,
                value=value,
                observed_at=entry.observed_at,
                verification_status=VerificationStatus.VERIFIED,
                raw_data={
                    "dataset": self._dataset.dataset_name,
                    "external_id": entry.external_id,
                },
                source_url="https://otwartedane.krakow.pl",
            )
            for feature_key, value in entry.features.items()
            if is_feature_key(feature_key)
        ]

    async def aclose(self) -> None:
        return None

    def _match(self, place: ExternalPlace) -> DatasetEntry | None:
        """Explicit OSM mapping first, then name plus proximity."""
        if place.provider_name == KRAKOW_PROVIDER_NAME:
            return next(
                (item for item in self._dataset.entries if item.external_id == place.external_id),
                None,
            )

        for entry in self._dataset.entries:
            if entry.osm_external_id and entry.osm_external_id == place.external_id:
                return entry
            same_name = normalize_name(entry.name) == normalize_name(place.name)
            if same_name and distance_meters(entry.location, place.location) < MAX_MATCH_DISTANCE_M:
                return entry

        return None
