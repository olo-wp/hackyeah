"""Fetches accessibility statements from official sites.

URLs always come from the allowlist, never from user input, so there is no
``scrape_url(anything)`` entry point (ARCHITECTURE section 50).
"""

import json
import logging
from importlib import resources
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from routeable_model import (
    DataSource,
    ExternalPlace,
    RawAccessibilityEvidence,
    SourceType,
)
from routeable_provider_core import (
    AccessibilityClassifier,
    HttpClient,
    SearchOptions,
    SourceDocument,
)

from .extraction import html_to_text

WEBSITE_PROVIDER_NAME = "website"

logger = logging.getLogger(__name__)


class AllowlistedSite(BaseModel):
    domain: str
    allowed: bool = False
    refresh_interval_hours: int = 24
    place_ids: list[str] = Field(default_factory=list)
    accessibility_pages: list[str] = Field(default_factory=list)


class Allowlist(BaseModel):
    sites: list[AllowlistedSite] = Field(default_factory=list)


def _load_allowlist(path: Path | None) -> list[AllowlistedSite]:
    if path is None:
        raw = (
            resources.files("routeable_provider_websites.config")
            .joinpath("allowlist.json")
            .read_text(encoding="utf-8")
        )
    else:
        raw = path.read_text(encoding="utf-8")

    allowlist = Allowlist.model_validate(json.loads(raw))
    return [site for site in allowlist.sites if site.allowed]


def _host_of(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return None
    return parsed.hostname.removeprefix("www.")


class WebsiteProvider:
    def __init__(
        self,
        allowlist_path: Path | None = None,
        user_agent: str = "RouteAble/0.1",
        timeout_s: float = 5.0,
        classifier: AccessibilityClassifier | None = None,
    ) -> None:
        self._sites = _load_allowlist(allowlist_path)
        self._http = HttpClient(user_agent=user_agent, timeout_s=timeout_s)
        self._classifier = classifier

    @property
    def name(self) -> str:
        return WEBSITE_PROVIDER_NAME

    @property
    def source(self) -> DataSource:
        return DataSource(
            id=WEBSITE_PROVIDER_NAME,
            type=SourceType.OFFICIAL_WEBSITE,
            name="Official website",
            license="site terms of use",
        )

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]:
        """Websites are not a discovery source; search belongs to OSM and the city dataset."""
        return []

    async def get_place(self, external_id: str) -> ExternalPlace | None:
        return None

    async def get_accessibility_data(
        self, place: ExternalPlace
    ) -> list[RawAccessibilityEvidence]:
        site = self._resolve_site(place)
        if site is None:
            return []

        if self._classifier is None:
            raise RuntimeError("An AI accessibility classifier is required for website data")
        documents: list[SourceDocument] = []
        for page in site.accessibility_pages:
            url = f"https://{site.domain}{page}"
            try:
                raw_html = await self._http.get_text(url)
            except Exception as error:
                logger.info("Skipping %s: %s", url, error)
                continue
            documents.append(SourceDocument(url, html_to_text(raw_html)))

        return await self._classifier.classify(place, documents)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _resolve_site(self, place: ExternalPlace) -> AllowlistedSite | None:
        place_id = f"{place.provider_name}:{place.external_id}"
        by_place_id = next((s for s in self._sites if place_id in s.place_ids), None)
        if by_place_id is not None:
            return by_place_id

        host = _host_of(place.website_url) if place.website_url else None
        return next((s for s in self._sites if s.domain == host), None) if host else None
