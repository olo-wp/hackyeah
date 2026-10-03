"""Compares observed facts against the user's functional requirements."""

from collections.abc import Callable
from typing import Any

from routeable_model import (
    AccessibilityFeature,
    AccessibilityPreferences,
    AccessibilityProfile,
    FeatureKey,
    FeatureStatus,
    PreferenceEvaluation,
    PreferenceResult,
    SurfaceValue,
)

ROUGH_SURFACES = {SurfaceValue.COBBLESTONE, SurfaceValue.GRAVEL, SurfaceValue.UNPAVED}


def _evaluate(
    key: FeatureKey,
    preference: Any,
    feature: AccessibilityFeature[Any],
    matches: Callable[[Any], bool],
) -> PreferenceEvaluation:
    if feature.status == FeatureStatus.CONFLICTING:
        result = PreferenceResult.NEEDS_VERIFICATION
    elif feature.value is None:
        result = PreferenceResult.UNKNOWN
    elif matches(feature.value):
        result = PreferenceResult.MEETS_PREFERENCE
    else:
        result = PreferenceResult.DOES_NOT_MEET_PREFERENCE

    return PreferenceEvaluation(
        key=key, preference=preference, observed_value=feature.value, result=result
    )


def evaluate_preferences(
    profile: AccessibilityProfile, preferences: AccessibilityPreferences
) -> list[PreferenceEvaluation]:
    """Never collapses into "accessible" / "not accessible" — the user decides."""
    evaluations: list[PreferenceEvaluation] = []

    if preferences.step_free_required:
        evaluations.append(
            _evaluate(
                FeatureKey.STEP_FREE_ENTRANCE,
                True,
                profile.entrance.step_free,
                lambda value: value is True,
            )
        )

    if preferences.elevator_required:
        evaluations.append(
            _evaluate(
                FeatureKey.ELEVATOR, True, profile.interior.elevator, lambda value: value is True
            )
        )

    if preferences.accessible_toilet_required:
        evaluations.append(
            _evaluate(
                FeatureKey.ACCESSIBLE_TOILET,
                True,
                profile.facilities.accessible_toilet,
                lambda value: value is True,
            )
        )

    if preferences.accessible_parking_required:
        evaluations.append(
            _evaluate(
                FeatureKey.ACCESSIBLE_PARKING,
                True,
                profile.surroundings.accessible_parking,
                lambda value: value is True,
            )
        )

    if preferences.seating_required:
        evaluations.append(
            _evaluate(
                FeatureKey.SEATING, True, profile.facilities.seating, lambda value: value is True
            )
        )

    if preferences.min_door_width_cm is not None:
        minimum = preferences.min_door_width_cm
        evaluations.append(
            _evaluate(
                FeatureKey.DOOR_WIDTH_CM,
                minimum,
                profile.entrance.door_width_cm,
                lambda value: value >= minimum,
            )
        )

    if preferences.max_threshold_cm is not None:
        maximum = preferences.max_threshold_cm
        evaluations.append(
            _evaluate(
                FeatureKey.THRESHOLD_CM,
                maximum,
                profile.entrance.threshold_cm,
                lambda value: value <= maximum,
            )
        )

    if preferences.avoid_cobblestone:
        evaluations.append(
            _evaluate(
                FeatureKey.SURFACE,
                "no cobblestone",
                profile.surroundings.surface,
                lambda value: value not in ROUGH_SURFACES,
            )
        )

    return evaluations
