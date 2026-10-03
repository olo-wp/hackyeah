"""Contradictions that only appear when two features are read together."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from routeable_model import AccessibilityFeature, FeatureKey, FeatureStatus

ResolvedFeatures = dict[FeatureKey, AccessibilityFeature[Any]]

THRESHOLD_LIMIT_CM = 6


@dataclass(frozen=True, slots=True)
class Violation:
    reason: str
    affected: tuple[FeatureKey, ...]


@dataclass(frozen=True, slots=True)
class CrossFeatureRule:
    id: str
    check: Callable[[ResolvedFeatures], Violation | None]


def _usable_value(features: ResolvedFeatures, key: FeatureKey) -> Any:
    feature = features.get(key)
    if feature is None or feature.status in (FeatureStatus.UNKNOWN, FeatureStatus.CONFLICTING):
        return None
    return feature.value


def _step_free_vs_steps(features: ResolvedFeatures) -> Violation | None:
    step_free = _usable_value(features, FeatureKey.STEP_FREE_ENTRANCE)
    steps = _usable_value(features, FeatureKey.ENTRANCE_STEPS)
    ramp = _usable_value(features, FeatureKey.RAMP)

    if step_free is True and isinstance(steps, int | float) and steps > 0 and ramp is not True:
        return Violation(
            reason=(
                "One source reports a step-free entrance while another reports "
                f"{steps:g} step(s) and no ramp"
            ),
            affected=(FeatureKey.STEP_FREE_ENTRANCE, FeatureKey.ENTRANCE_STEPS),
        )
    return None


def _step_free_vs_threshold(features: ResolvedFeatures) -> Violation | None:
    step_free = _usable_value(features, FeatureKey.STEP_FREE_ENTRANCE)
    threshold = _usable_value(features, FeatureKey.THRESHOLD_CM)

    if step_free is True and isinstance(threshold, int | float) and threshold > THRESHOLD_LIMIT_CM:
        return Violation(
            reason=(
                "Entrance is reported as step-free but the threshold is "
                f"{threshold:g} cm"
            ),
            affected=(FeatureKey.STEP_FREE_ENTRANCE, FeatureKey.THRESHOLD_CM),
        )
    return None


CROSS_FEATURE_RULES: tuple[CrossFeatureRule, ...] = (
    CrossFeatureRule("step_free_vs_steps", _step_free_vs_steps),
    CrossFeatureRule("step_free_vs_threshold", _step_free_vs_threshold),
)


def apply_cross_feature_rules(features: ResolvedFeatures) -> list[str]:
    """Marks every feature touched by a broken rule as ``conflicting``."""
    reasons: list[str] = []

    for rule in CROSS_FEATURE_RULES:
        violation = rule.check(features)
        if violation is None:
            continue

        reasons.append(violation.reason)
        for key in violation.affected:
            feature = features.get(key)
            if feature is None:
                continue
            features[key] = feature.model_copy(
                update={
                    "value": None,
                    "status": FeatureStatus.CONFLICTING,
                    "confidence": None,
                    "conflict_reason": violation.reason,
                }
            )

    return reasons
