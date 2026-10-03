"""The contract every data source adapter implements."""

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field
from routeable_model import (
    DataSource,
    ExternalPlace,
    GeoLocation,
    RawAccessibilityEvidence,
)


class SearchOptions(BaseModel):
    location: GeoLocation | None = None
    city: str | None = None
    limit: int = Field(default=10, ge=1, le=25)


@runtime_checkable
class AccessibilityProvider(Protocol):
    """Adapters map their own shape onto the shared model.

    A provider never decides whether a place is "accessible" — it only reports facts.
    """

    @property
    def name(self) -> str:
        """Stable id used as the ``provider`` segment of a RouteAble place id."""
        ...

    @property
    def source(self) -> DataSource:
        """Provenance attached to every piece of evidence this provider returns."""
        ...

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]: ...

    async def get_place(self, external_id: str) -> ExternalPlace | None: ...

    async def get_accessibility_data(
        self, place: ExternalPlace
    ) -> list[RawAccessibilityEvidence]: ...

    async def aclose(self) -> None: ...
