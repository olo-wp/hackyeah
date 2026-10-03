"""Accessibility data intelligence: normalization, conflicts, confidence, preferences."""

from .community import COMMUNITY_FRESH_WINDOW_DAYS, summarize_contributions
from .confidence import (
    SOURCE_CONFIDENCE,
    calculate_confidence,
    freshness_modifier,
    score_evidence,
    to_confidence_level,
)
from .conflicts import CROSS_FEATURE_RULES, apply_cross_feature_rules
from .identity import is_same_place
from .place_id import ParsedPlaceId, build_place_id, parse_place_id
from .preferences import evaluate_preferences
from .profile_builder import build_accessibility_profile, resolve_features
from .resolve import DEFAULT_STALE_AFTER_DAYS, empty_feature, resolve_feature
from .service import (
    AccessibilityService,
    PlaceAccessibilityResult,
    PlaceNotFoundError,
    PlaceSearchResult,
    ProviderStatus,
    ProviderStatusValue,
)
from .store import EvidenceStore, InMemoryEvidenceStore

__all__ = [
    "COMMUNITY_FRESH_WINDOW_DAYS",
    "CROSS_FEATURE_RULES",
    "DEFAULT_STALE_AFTER_DAYS",
    "SOURCE_CONFIDENCE",
    "AccessibilityService",
    "EvidenceStore",
    "InMemoryEvidenceStore",
    "ParsedPlaceId",
    "PlaceAccessibilityResult",
    "PlaceNotFoundError",
    "PlaceSearchResult",
    "ProviderStatus",
    "ProviderStatusValue",
    "apply_cross_feature_rules",
    "build_accessibility_profile",
    "build_place_id",
    "calculate_confidence",
    "empty_feature",
    "evaluate_preferences",
    "freshness_modifier",
    "is_same_place",
    "parse_place_id",
    "resolve_feature",
    "resolve_features",
    "score_evidence",
    "summarize_contributions",
    "to_confidence_level",
]
