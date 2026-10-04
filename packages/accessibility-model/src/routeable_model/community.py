"""Community contributions — anonymous, uncertain answers kept apart from evidence."""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from .features import FeatureKey, SurfaceValue

# Vote options per feature; `None` marks a yes/no question. Non-booleans use buckets.
COMMUNITY_FEATURE_OPTIONS: dict[FeatureKey, tuple[str, ...] | None] = {
    FeatureKey.STEP_FREE_ENTRANCE: None,
    FeatureKey.ENTRANCE_STEPS: ("none", "few", "some", "many"),
    FeatureKey.RAMP: None,
    FeatureKey.THRESHOLD_CM: ("none", "small", "high"),
    FeatureKey.DOOR_WIDTH_CM: ("narrow", "wide"),
    FeatureKey.ELEVATOR: None,
    FeatureKey.INTERIOR_STAIRS: None,
    FeatureKey.ACCESSIBLE_TOILET: None,
    FeatureKey.SEATING: None,
    FeatureKey.SURFACE: tuple(s.value for s in SurfaceValue if s is not SurfaceValue.UNKNOWN),
    FeatureKey.CURB: None,
    FeatureKey.ACCESSIBLE_PARKING: None,
}


class CommunityAnswer(BaseModel):
    feature_key: FeatureKey
    value: bool | str

    @model_validator(mode="after")
    def _value_matches_feature(self) -> "CommunityAnswer":
        options = COMMUNITY_FEATURE_OPTIONS[self.feature_key]
        if options is None:
            if not isinstance(self.value, bool):
                raise ValueError(f"{self.feature_key.value} expects a true/false answer")
        elif isinstance(self.value, bool) or self.value not in options:
            allowed = ", ".join(options)
            raise ValueError(f"{self.feature_key.value} expects one of: {allowed}")
        return self


class NewCommunityContribution(CommunityAnswer):
    place_id: str


class CommunityContribution(NewCommunityContribution):
    id: str
    submitted_at: datetime


class CommunityFeatureSummary(BaseModel):
    feature_key: FeatureKey
    total_responses: int = 0
    distribution: dict[str, int] = Field(default_factory=dict)
    top_value: bool | str | None = None
    latest_value: bool | str | None = None
    last_submitted_at: datetime | None = None


class CommunitySummary(BaseModel):
    place_id: str
    features: list[CommunityFeatureSummary]
