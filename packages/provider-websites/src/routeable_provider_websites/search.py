"""Google Search research for every place, independent of its discovery provider."""

from routeable_model import DataSource, ExternalPlace, RawAccessibilityEvidence, SourceType
from routeable_provider_core import GeminiAccessibilityClassifier, SearchOptions


class GoogleSearchProvider:
    def __init__(self, classifier: GeminiAccessibilityClassifier) -> None:
        self._classifier = classifier

    @property
    def name(self) -> str:
        return "google_search"

    @property
    def source(self) -> DataSource:
        return DataSource(
            id=self.name,
            type=SourceType.GOOGLE_SEARCH,
            name="Google Search (Gemini)",
            license="source site terms of use",
        )

    async def search_places(
        self, query: str, options: SearchOptions | None = None
    ) -> list[ExternalPlace]:
        return []

    async def get_place(self, external_id: str) -> ExternalPlace | None:
        return None

    async def get_accessibility_data(self, place: ExternalPlace) -> list[RawAccessibilityEvidence]:
        return await self._classifier.search_accessibility(place)

    async def aclose(self) -> None:
        # This provider owns the shared classifier; OSM and website adapters borrow it.
        await self._classifier.aclose()
