"""Builds the derived accessibility profile. Evidence stays the source of truth."""

from collections import defaultdict
from datetime import datetime
from typing import TypeVar

from pydantic import ValidationError
from routeable_model import (
    AccessibilityFeature,
    AccessibilityProfile,
    EntranceFeatures,
    Evidence,
    FacilityFeatures,
    FeatureKey,
    FeatureStatus,
    InteriorFeatures,
    ProfileMetadata,
    SurfaceValue,
    SurroundingFeatures,
)

from .conflicts import ResolvedFeatures, apply_cross_feature_rules
from .resolve import DEFAULT_STALE_AFTER_DAYS, empty_feature, resolve_feature

T = TypeVar("T")


def group_by_feature(evidence: list[Evidence]) -> dict[FeatureKey, list[Evidence]]:
    grouped: dict[FeatureKey, list[Evidence]] = defaultdict(list)
    for item in evidence:
        grouped[item.feature_key].append(item)
    return grouped


def resolve_features(
    evidence: list[Evidence],
    now: datetime,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> ResolvedFeatures:
    grouped = group_by_feature(evidence)
    resolved: ResolvedFeatures = {
        key: resolve_feature(key, grouped.get(key, []), now, stale_after_days)
        for key in FeatureKey
    }
    apply_cross_feature_rules(resolved)
    return resolved


def _typed(
    features: ResolvedFeatures,
    key: FeatureKey,
    model: type[AccessibilityFeature[T]],
) -> AccessibilityFeature[T]:
    """Re-validates against the feature's declared value type.

    External sources can emit something unexpected (``door_width_cm = "wide"``); that is a
    data problem, not a crash, so it degrades to ``conflicting`` with the evidence kept.
    """
    feature = features.get(key) or empty_feature(key)
    try:
        return model.model_validate(feature.model_dump())
    except ValidationError:
        return model(
            key=key,
            value=None,
            status=FeatureStatus.CONFLICTING,
            confidence=None,
            evidence=feature.evidence,
            conflict_reason="A source reported a value that does not match the expected type",
        )


def build_accessibility_profile(
    place_id: str,
    evidence: list[Evidence],
    now: datetime,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> AccessibilityProfile:
    features = resolve_features(evidence, now, stale_after_days)

    return AccessibilityProfile(
        place_id=place_id,
        entrance=EntranceFeatures(
            step_free=_typed(features, FeatureKey.STEP_FREE_ENTRANCE, AccessibilityFeature[bool]),
            steps=_typed(features, FeatureKey.ENTRANCE_STEPS, AccessibilityFeature[int]),
            ramp=_typed(features, FeatureKey.RAMP, AccessibilityFeature[bool]),
            threshold_cm=_typed(features, FeatureKey.THRESHOLD_CM, AccessibilityFeature[float]),
            door_width_cm=_typed(features, FeatureKey.DOOR_WIDTH_CM, AccessibilityFeature[float]),
        ),
        interior=InteriorFeatures(
            elevator=_typed(features, FeatureKey.ELEVATOR, AccessibilityFeature[bool]),
            stairs=_typed(features, FeatureKey.INTERIOR_STAIRS, AccessibilityFeature[bool]),
        ),
        facilities=FacilityFeatures(
            accessible_toilet=_typed(
                features, FeatureKey.ACCESSIBLE_TOILET, AccessibilityFeature[bool]
            ),
            seating=_typed(features, FeatureKey.SEATING, AccessibilityFeature[bool]),
        ),
        surroundings=SurroundingFeatures(
            surface=_typed(features, FeatureKey.SURFACE, AccessibilityFeature[SurfaceValue]),
            curb=_typed(features, FeatureKey.CURB, AccessibilityFeature[bool]),
            accessible_parking=_typed(
                features, FeatureKey.ACCESSIBLE_PARKING, AccessibilityFeature[bool]
            ),
        ),
        metadata=ProfileMetadata(
            source_count=len({item.source.id for item in evidence}),
            evidence_count=len(evidence),
            last_updated=max((item.retrieved_at for item in evidence), default=None),
        ),
    )
