"""Turns raw observations into a single feature, surfacing disagreement."""

import json
from datetime import datetime
from typing import Any

from routeable_model import (
    AccessibilityFeature,
    Evidence,
    FeatureKey,
    FeatureStatus,
)

from .confidence import age_days, calculate_confidence

DEFAULT_STALE_AFTER_DAYS = 180


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def empty_feature(key: FeatureKey) -> AccessibilityFeature[Any]:
    return AccessibilityFeature[Any](key=key, value=None, status=FeatureStatus.UNKNOWN)


def resolve_feature(
    key: FeatureKey,
    evidence: list[Evidence],
    now: datetime,
    stale_after_days: int = DEFAULT_STALE_AFTER_DAYS,
) -> AccessibilityFeature[Any]:
    """Missing data stays ``unknown``; disagreement stays ``conflicting``."""
    if not evidence:
        return empty_feature(key)

    distinct: dict[str, Any] = {_canonical(item.value): item.value for item in evidence}

    if len(distinct) > 1:
        rendered = " vs ".join(distinct.keys())
        return AccessibilityFeature[Any](
            key=key,
            value=None,
            status=FeatureStatus.CONFLICTING,
            confidence=None,
            evidence=evidence,
            conflict_reason=f"Sources disagree: {rendered}",
        )

    value = next(iter(distinct.values()))
    newest = max(item.retrieved_at for item in evidence)
    is_stale = age_days(newest, now) > stale_after_days

    return AccessibilityFeature[Any](
        key=key,
        value=value,
        status=FeatureStatus.STALE if is_stale else FeatureStatus.CONFIRMED,
        confidence=calculate_confidence(evidence, now),
        evidence=evidence,
    )
