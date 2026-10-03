"""Functional preferences — RouteAble never stores a disability label."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .features import FeatureKey


class AccessibilityPreferences(BaseModel):
    step_free_required: bool = False
    elevator_required: bool = False
    accessible_toilet_required: bool = False
    accessible_parking_required: bool = False
    seating_required: bool = False
    avoid_cobblestone: bool = False
    min_door_width_cm: float | None = Field(default=None, ge=40, le=200)
    max_threshold_cm: float | None = Field(default=None, ge=0, le=50)


class PreferenceResult(StrEnum):
    MEETS_PREFERENCE = "meets_preference"
    DOES_NOT_MEET_PREFERENCE = "does_not_meet_preference"
    UNKNOWN = "unknown"
    NEEDS_VERIFICATION = "needs_verification"


class PreferenceEvaluation(BaseModel):
    key: FeatureKey
    preference: Any = None
    observed_value: Any = None
    result: PreferenceResult
