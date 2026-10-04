"""Search de-duplication: a curated DB place (with its seeded evidence) must win
over a live provider duplicate so its id — and therefore its evidence — is what the
UI links to.
"""

import asyncio

from routeable_engine import AccessibilityService, InMemoryEvidenceStore
from routeable_model import (
    DataSource,
    ExternalIds,
    ExternalPlace,
    GeoLocation,
    Place,
    PlaceCategory,
    RawAccessibilityEvidence,
    SourceType,
)
from routeable_provider_core import ProviderRegistry, SearchOptions

BARBAKAN = GeoLocation(lat=50.0659, lng=19.9416)


class StubProvider:
    """Minimal live provider returning a fixed set of results."""

    def __init__(self, name: str, source_type: SourceType, results: list[ExternalPlace]) -> None:
        self._name = name
        self._source_type = source_type
        self._results = results

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> DataSource:
        return DataSource(id=self._name, type=self._source_type, name=self._name)

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]:
        return list(self._results)

    async def get_place(self, external_id: str) -> ExternalPlace | None:
        return None

    async def get_accessibility_data(
        self, place: ExternalPlace
    ) -> list[RawAccessibilityEvidence]:
        return []

    async def aclose(self) -> None:
        return None


def _service(store: InMemoryEvidenceStore, providers: list[StubProvider]) -> AccessibilityService:
    return AccessibilityService(registry=ProviderRegistry(providers), store=store)


def test_curated_store_place_wins_over_live_duplicate() -> None:
    store = InMemoryEvidenceStore()
    curated = Place(
        id="krakow:barbakan",
        name="Barbakan – Muzeum Krakowa",
        category=PlaceCategory.MUSEUM,
        location=BARBAKAN,
        external_ids=ExternalIds(city_dataset="barbakan"),
    )
    asyncio.run(store.save_place(curated))

    osm_hit = ExternalPlace(
        external_id="relation:13562708",
        provider_name="osm",
        name="Barbakan",
        category=PlaceCategory.ATTRACTION,
        location=BARBAKAN,
    )
    provider = StubProvider("osm", SourceType.OPENSTREETMAP, [osm_hit])

    result = asyncio.run(
        _service(store, [provider]).search_places("barbakan", SearchOptions(limit=10))
    )

    assert [place.id for place in result.results] == ["krakow:barbakan"]


def test_live_only_place_is_returned() -> None:
    store = InMemoryEvidenceStore()
    osm_hit = ExternalPlace(
        external_id="node:1",
        provider_name="osm",
        name="Some Café",
        category=PlaceCategory.RESTAURANT,
        location=GeoLocation(lat=50.06, lng=19.94),
    )
    provider = StubProvider("osm", SourceType.OPENSTREETMAP, [osm_hit])

    result = asyncio.run(
        _service(store, [provider]).search_places("café", SearchOptions(limit=10))
    )

    assert [place.id for place in result.results] == ["osm:node:1"]
