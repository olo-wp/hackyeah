"""MCP tools over the shared AccessibilityService.

MCP is an interface, not a database: it holds no business logic of its own and calls
exactly the same service the REST API uses (ARCHITECTURE section 63.6).
"""

from typing import Any

from mcp.server.mcpserver import MCPServer

from routeable_engine import AccessibilityService
from routeable_model import (
    AccessibilityPreferences,
    FeatureKey,
    NewAccessibilityReport,
    ReportIssueType,
)
from routeable_provider_core import SearchOptions

INSTRUCTIONS = """
RouteAble exposes accessibility facts about places in Krakow.

Rules when using this data:
- `unknown` means the information is missing. It never means "accessible".
- `conflicting` means sources disagree; present both sides instead of picking one.
- Every value carries its source, retrieval date and confidence — cite them.
""".strip()


def create_server(service: AccessibilityService) -> MCPServer:
    mcp = MCPServer("routeable", instructions=INSTRUCTIONS)

    @mcp.tool()
    async def search_places(
        query: str, city: str = "Kraków", limit: int = 10
    ) -> dict[str, Any]:
        """Find places by name. Returns candidates with their RouteAble `place_id`."""
        result = await service.search_places(query, SearchOptions(city=city, limit=limit))
        return result.model_dump(mode="json")

    @mcp.tool()
    async def get_place_accessibility(
        place_id: str,
        step_free_required: bool = False,
        elevator_required: bool = False,
        accessible_toilet_required: bool = False,
        min_door_width_cm: float | None = None,
        avoid_cobblestone: bool = False,
    ) -> dict[str, Any]:
        """Return the accessibility profile for a place.

        Preferences only highlight and order relevant facts — they never turn the answer
        into "accessible" or "not accessible".
        """
        preferences = AccessibilityPreferences(
            step_free_required=step_free_required,
            elevator_required=elevator_required,
            accessible_toilet_required=accessible_toilet_required,
            min_door_width_cm=min_door_width_cm,
            avoid_cobblestone=avoid_cobblestone,
        )
        result = await service.get_place_accessibility(place_id, preferences)
        return result.model_dump(mode="json")

    @mcp.tool()
    async def get_accessibility_evidence(
        place_id: str, feature: FeatureKey | None = None
    ) -> dict[str, Any]:
        """Return the raw evidence behind a feature, including source and retrieval date."""
        evidence = await service.get_evidence(place_id, feature)
        return {
            "place_id": place_id,
            "feature": feature.value if feature else None,
            "evidence": [item.model_dump(mode="json") for item in evidence],
        }

    @mcp.tool()
    async def report_accessibility_issue(
        place_id: str, feature: FeatureKey, issue_type: ReportIssueType, message: str
    ) -> dict[str, Any]:
        """Report incorrect, outdated, missing or conflicting information."""
        report = await service.report_issue(
            NewAccessibilityReport(
                place_id=place_id,
                feature_key=feature,
                issue_type=issue_type,
                message=message,
            )
        )
        return report.model_dump(mode="json")

    return mcp
