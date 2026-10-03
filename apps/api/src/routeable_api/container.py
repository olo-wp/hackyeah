"""Wires providers, storage and the accessibility service together."""

import logging
from dataclasses import dataclass

from psycopg_pool import AsyncConnectionPool

from routeable_database import PostgresEvidenceStore, create_pool
from routeable_engine import AccessibilityService, EvidenceStore, InMemoryEvidenceStore
from routeable_provider_core import GeminiAccessibilityClassifier, ProviderRegistry
from routeable_provider_krakow import KrakowOpenDataProvider
from routeable_provider_osm import OsmProvider
from routeable_provider_websites import GoogleSearchProvider, WebsiteProvider

from .config import Settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Container:
    service: AccessibilityService
    registry: ProviderRegistry
    pool: AsyncConnectionPool | None

    async def aclose(self) -> None:
        await self.registry.aclose()
        if self.pool is not None:
            await self.pool.close()


def build_registry(settings: Settings) -> ProviderRegistry:
    classifier = GeminiAccessibilityClassifier(
        api_key=settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None,
        model=settings.gemini_model,
        timeout_s=settings.gemini_timeout_s,
        max_input_chars=settings.gemini_max_input_chars,
        fallback_model=settings.gemini_fallback_model,
    )
    return ProviderRegistry(
        [
            OsmProvider(
                nominatim_url=settings.nominatim_url,
                overpass_url=settings.osm_overpass_url,
                user_agent=settings.user_agent,
                timeout_s=settings.provider_timeout_s,
                classifier=classifier,
            ),
            KrakowOpenDataProvider(),
            WebsiteProvider(
                user_agent=settings.user_agent,
                timeout_s=settings.provider_timeout_s,
                classifier=classifier,
            ),
            GoogleSearchProvider(classifier),
        ]
    )


async def build_container(settings: Settings) -> Container:
    pool: AsyncConnectionPool | None = None
    store: EvidenceStore

    if settings.database_url:
        pool = create_pool(settings.database_url)
        await pool.open(wait=True)
        store = PostgresEvidenceStore(pool)
    else:
        logger.warning("DATABASE_URL not set — falling back to the in-memory evidence store")
        store = InMemoryEvidenceStore()

    registry = build_registry(settings)

    return Container(
        service=AccessibilityService(
            registry=registry,
            store=store,
            cache_ttl_hours=settings.provider_cache_ttl_hours,
            stale_after_days=settings.stale_after_days,
        ),
        registry=registry,
        pool=pool,
    )
