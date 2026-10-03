"""The aggregated, read-only view of a place's accessibility."""

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from .evidence import Evidence
from .features import ConfidenceLevel, FeatureKey, FeatureStatus, SurfaceValue

T = TypeVar("T")


class AccessibilityFeature(BaseModel, Generic[T]):
    key: FeatureKey
    value: T | None = None
    status: FeatureStatus = FeatureStatus.UNKNOWN
    confidence: ConfidenceLevel | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    conflict_reason: str | None = Field(
        default=None, description="Set when status is 'conflicting'"
    )


class EntranceFeatures(BaseModel):
    step_free: AccessibilityFeature[bool]
    steps: AccessibilityFeature[int]
    ramp: AccessibilityFeature[bool]
    threshold_cm: AccessibilityFeature[float]
    door_width_cm: AccessibilityFeature[float]


class InteriorFeatures(BaseModel):
    elevator: AccessibilityFeature[bool]
    stairs: AccessibilityFeature[bool]


class FacilityFeatures(BaseModel):
    accessible_toilet: AccessibilityFeature[bool]
    seating: AccessibilityFeature[bool]


class SurroundingFeatures(BaseModel):
    surface: AccessibilityFeature[SurfaceValue]
    curb: AccessibilityFeature[bool]
    accessible_parking: AccessibilityFeature[bool]


class ProfileMetadata(BaseModel):
    source_count: int = 0
    evidence_count: int = 0
    last_updated: datetime | None = None


class AccessibilityProfile(BaseModel):
    place_id: str
    entrance: EntranceFeatures
    interior: InteriorFeatures
    facilities: FacilityFeatures
    surroundings: SurroundingFeatures
    metadata: ProfileMetadata = Field(default_factory=ProfileMetadata)
