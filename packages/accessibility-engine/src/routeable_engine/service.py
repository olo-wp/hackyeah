"""The single place where ingestion, normalization, conflicts and confidence live.

REST API and MCP server are both thin wrappers over this service.
"""

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel
from routeable_model import (
    AccessibilityPreferences,
    AccessibilityProfile,
    AccessibilityReport,
    DataSource,
    Evidence,
    ExternalIds,
    ExternalPlace,
    FeatureKey,
    NewAccessibilityReport,
    Place,
    PreferenceEvaluation,
    SourceType,
)
from routeable_provider_core import AccessibilityProvider, ProviderRegistry, SearchOptions

from .identity import is_same_place
from .place_id import build_place_id, parse_place_id
from .preferences import evaluate_preferences
from .profile_builder import build_accessibility_profile
from .store import EvidenceStore

logger = logging.getLogger(__name__)


class PlaceNotFoundError(LookupError):
    def __init__(self, place_id: str) -> None:
        super().__init__(f'Place "{place_id}" was not found')
        self.place_id = place_id


class ProviderStatusValue(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"
    NOT_APPLICABLE = "not_applicable"


class ProviderStatus(BaseModel):
    provider: str
    status: ProviderStatusValue
    last_fetched_at: datetime | None = None
    error: str | None = None


class PlaceSearchResult(BaseModel):
    results: list[Place]
    provider_status: list[ProviderStatus]


class PlaceAccessibilityResult(BaseModel):
    place: Place
    profile: AccessibilityProfile
    preference_evaluation: list[PreferenceEvaluation]
    provider_status: list[ProviderStatus]


class AccessibilityService:
    def __init__(
        self,
        registry: ProviderRegistry,
        store: EvidenceStore,
        cache_ttl_hours: int = 24,
        stale_after_days: int = 180,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._registry = registry
        self._store = store
        self._cache_ttl = timedelta(hours=cache_ttl_hours)
        self._stale_after_days = stale_after_days
        self._now = clock or (lambda: datetime.now(UTC))

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> PlaceSearchResult:
        options = options or SearchOptions()
        providers = self._registry.get_providers()

        results = await asyncio.gather(
            *(provider.search_places(query, options) for provider in providers),
            return_exceptions=True,
        )

        provider_status: list[ProviderStatus] = []
        candidates: list[tuple[AccessibilityProvider, ExternalPlace]] = []

        for provider, result in zip(providers, results, strict=True):
            if isinstance(result, BaseException):
                logger.warning("Search failed for provider %s: %s", provider.name, result)
                provider_status.append(
                    ProviderStatus(
                        provider=provider.name,
                        status=ProviderStatusValue.FAILED,
                        error=str(result),
                    )
                )
                continue

            provider_status.append(
                ProviderStatus(
                    provider=provider.name,
                    status=ProviderStatusValue.SUCCESS,
                    last_fetched_at=self._now(),
                )
            )
            candidates.extend((provider, place) for place in result)

        deduped: list[tuple[AccessibilityProvider, ExternalPlace]] = []
        for provider, place in candidates:
            if not any(is_same_place(kept, place) for _, kept in deduped):
                deduped.append((provider, place))

        places = [_to_place(provider, place) for provider, place in deduped[: options.limit]]
        for place in places:
            await self._store.save_place(place)

        return PlaceSearchResult(results=places, provider_status=provider_status)

    async def get_place(self, place_id: str) -> Place:
        provider_name, external_id = parse_place_id(place_id)
        owner = self._registry.get(provider_name)

        if owner is not None:
            try:
                external = await owner.get_place(external_id)
            except Exception as error:  # noqa: BLE001 - a dead source must not 500 the request
                logger.warning("get_place failed for provider %s: %s", owner.name, error)
                external = None

            if external is not None:
                place = _to_place(owner, external)
                await self._store.save_place(place)
                return place

        cached = await self._store.get_place(place_id)
        if cached is None:
            raise PlaceNotFoundError(place_id)
        return cached

    async def get_place_accessibility(
        self, place_id: str, preferences: AccessibilityPreferences | None = None
    ) -> PlaceAccessibilityResult:
        place = await self.get_place(place_id)
        provider_status = await self._collect_evidence(place)
        evidence = await self._store.get_evidence(place_id)

        profile = build_accessibility_profile(
            place_id, evidence, self._now(), self._stale_after_days
        )

        return PlaceAccessibilityResult(
            place=place,
            profile=profile,
            preference_evaluation=evaluate_preferences(
                profile, preferences or AccessibilityPreferences()
            ),
            provider_status=provider_status,
        )

    async def get_evidence(
        self, place_id: str, feature_key: FeatureKey | None = None
    ) -> list[Evidence]:
        place = await self.get_place(place_id)
        await self._collect_evidence(place)
        return await self._store.get_evidence(place_id, feature_key)

    async def report_issue(self, input_report: NewAccessibilityReport) -> AccessibilityReport:
        """Reports enter as unverified input and never overwrite confirmed evidence."""
        report = AccessibilityReport(
            **input_report.model_dump(), id=str(uuid4()), created_at=self._now()
        )
        await self._store.save_report(report)
        return report

    async def list_reports(self, place_id: str | None = None) -> list[AccessibilityReport]:
        return await self._store.list_reports(place_id)

    async def _collect_evidence(self, place: Place) -> list[ProviderStatus]:
        external = _to_external_place(place)
        providers = self._registry.get_providers()
        return list(
            await asyncio.gather(
                *(self._refresh_provider(provider, place, external) for provider in providers)
            )
        )

    async def _refresh_provider(
        self, provider: AccessibilityProvider, place: Place, external: ExternalPlace
    ) -> ProviderStatus:
        last_fetched_at = await self._store.get_last_fetched_at(place.id, provider.name)

        if last_fetched_at is not None and self._is_fresh(last_fetched_at):
            return ProviderStatus(
                provider=provider.name,
                status=ProviderStatusValue.CACHED,
                last_fetched_at=last_fetched_at,
            )

        try:
            raw = await provider.get_accessibility_data(external)
        except Exception as error:  # noqa: BLE001 - keep cached evidence, never assume access
            logger.warning("Provider %s failed for %s: %s", provider.name, place.id, error)
            return ProviderStatus(
                provider=provider.name,
                status=ProviderStatusValue.FAILED,
                last_fetched_at=last_fetched_at,
                error=str(error),
            )

        retrieved_at = self._now()
        evidence = [
            Evidence(
                id=str(uuid4()),
                place_id=place.id,
                feature_key=item.feature_key,
                source=DataSource(
                    id=provider.name,
                    type=provider.source.type,
                    name=provider.source.name,
                    url=item.source_url or provider.source.url,
                    license=provider.source.license,
                ),
                value=item.value,
                retrieved_at=retrieved_at,
                observed_at=item.observed_at,
                verification_status=item.verification_status,
                raw_data=item.raw_data,
            )
            for item in raw
        ]

        await self._store.replace_provider_evidence(place.id, provider.name, evidence)
        await self._store.set_last_fetched_at(place.id, provider.name, retrieved_at)

        return ProviderStatus(
            provider=provider.name,
            status=ProviderStatusValue.SUCCESS if raw else ProviderStatusValue.NOT_APPLICABLE,
            last_fetched_at=retrieved_at,
        )

    def _is_fresh(self, timestamp: datetime) -> bool:
        reference = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=UTC)
        return self._now() - reference < self._cache_ttl


def _to_place(provider: AccessibilityProvider, external: ExternalPlace) -> Place:
    external_ids = ExternalIds(website=external.website_url)
    if provider.source.type == SourceType.OPENSTREETMAP:
        external_ids.osm = external.external_id
    if provider.source.type in (SourceType.CITY_OPEN_DATA, SourceType.DEMO_DATA):
        external_ids.city_dataset = external.external_id

    return Place(
        id=build_place_id(provider.name, external.external_id),
        name=external.name,
        category=external.category,
        address=external.address,
        location=external.location,
        external_ids=external_ids,
    )


def _to_external_place(place: Place) -> ExternalPlace:
    provider_name, external_id = parse_place_id(place.id)
    return ExternalPlace(
        external_id=external_id,
        provider_name=provider_name,
        name=place.name,
        category=place.category,
        address=place.address,
        location=place.location,
        website_url=place.external_ids.website,
    )
