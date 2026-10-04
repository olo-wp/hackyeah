"""Storage contract plus an in-memory implementation for local runs and tests."""

import unicodedata
from datetime import datetime
from typing import Protocol

from routeable_model import (
    AccessibilityReport,
    CommunityContribution,
    Evidence,
    FeatureKey,
    Place,
)


class EvidenceStore(Protocol):
    async def save_place(self, place: Place) -> None: ...

    async def get_place(self, place_id: str) -> Place | None: ...

    async def search_places(self, query: str, limit: int) -> list[Place]: ...

    async def replace_provider_evidence(
        self, place_id: str, provider_name: str, evidence: list[Evidence]
    ) -> None:
        """Replaces everything a given provider previously said about a place."""
        ...

    async def get_evidence(
        self, place_id: str, feature_key: FeatureKey | None = None
    ) -> list[Evidence]: ...

    async def get_last_fetched_at(self, place_id: str, provider_name: str) -> datetime | None: ...

    async def set_last_fetched_at(
        self, place_id: str, provider_name: str, at: datetime
    ) -> None: ...

    async def save_report(self, report: AccessibilityReport) -> None: ...

    async def list_reports(self, place_id: str | None = None) -> list[AccessibilityReport]: ...

    async def add_community_contribution(self, contribution: CommunityContribution) -> None: ...

    async def get_community_contributions(
        self,
        place_id: str,
        feature_key: FeatureKey | None = None,
        since: datetime | None = None,
    ) -> list[CommunityContribution]: ...


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


class InMemoryEvidenceStore:
    """Zero-dependency store so the API and MCP server run without Postgres."""

    def __init__(self) -> None:
        self._places: dict[str, Place] = {}
        self._evidence: dict[str, list[Evidence]] = {}
        self._fetched_at: dict[tuple[str, str], datetime] = {}
        self._reports: list[AccessibilityReport] = []
        self._community: list[CommunityContribution] = []

    async def save_place(self, place: Place) -> None:
        self._places[place.id] = place

    async def get_place(self, place_id: str) -> Place | None:
        return self._places.get(place_id)

    async def search_places(self, query: str, limit: int) -> list[Place]:
        needle = _normalize(query)
        matches = [p for p in self._places.values() if needle in _normalize(p.name)]
        return matches[:limit]

    async def replace_provider_evidence(
        self, place_id: str, provider_name: str, evidence: list[Evidence]
    ) -> None:
        kept = [e for e in self._evidence.get(place_id, []) if e.source.id != provider_name]
        self._evidence[place_id] = kept + evidence

    async def get_evidence(
        self, place_id: str, feature_key: FeatureKey | None = None
    ) -> list[Evidence]:
        items = self._evidence.get(place_id, [])
        if feature_key is None:
            return list(items)
        return [item for item in items if item.feature_key == feature_key]

    async def get_last_fetched_at(self, place_id: str, provider_name: str) -> datetime | None:
        return self._fetched_at.get((place_id, provider_name))

    async def set_last_fetched_at(self, place_id: str, provider_name: str, at: datetime) -> None:
        self._fetched_at[(place_id, provider_name)] = at

    async def save_report(self, report: AccessibilityReport) -> None:
        self._reports.append(report)

    async def list_reports(self, place_id: str | None = None) -> list[AccessibilityReport]:
        if place_id is None:
            return list(self._reports)
        return [report for report in self._reports if report.place_id == place_id]

    async def add_community_contribution(self, contribution: CommunityContribution) -> None:
        self._community.append(contribution)

    async def get_community_contributions(
        self,
        place_id: str,
        feature_key: FeatureKey | None = None,
        since: datetime | None = None,
    ) -> list[CommunityContribution]:
        items = [c for c in self._community if c.place_id == place_id]
        if feature_key is not None:
            items = [c for c in items if c.feature_key == feature_key]
        if since is not None:
            items = [c for c in items if c.submitted_at >= since]
        return sorted(items, key=lambda c: c.submitted_at, reverse=True)
