"""Community contributions — anonymous, uncertain answers kept apart from evidence."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class DoorstepLevel(StrEnum):
    NONE = "none"
    SMALL = "small"
    HIGH = "high"


class CommunityFeatureKey(StrEnum):
    """Questions users can answer. Separate from provider `FeatureKey` on purpose."""

    ACCESSIBLE_PARKING = "accessible_parking"
    ACCESSIBLE_TOILET = "accessible_toilet"
    STEP_FREE_ENTRANCE = "step_free_entrance"
    RAMP = "ramp"
    ELEVATOR = "elevator"
    DOORSTEP = "doorstep"


# The value type each question accepts; everything is boolean except the 3-way doorstep.
COMMUNITY_FEATURE_VALUES: dict[CommunityFeatureKey, type] = {
    CommunityFeatureKey.ACCESSIBLE_PARKING: bool,
    CommunityFeatureKey.ACCESSIBLE_TOILET: bool,
    CommunityFeatureKey.STEP_FREE_ENTRANCE: bool,
    CommunityFeatureKey.RAMP: bool,
    CommunityFeatureKey.ELEVATOR: bool,
    CommunityFeatureKey.DOORSTEP: DoorstepLevel,
}


class CommunityAnswer(BaseModel):
    feature_key: CommunityFeatureKey
    value: bool | DoorstepLevel

    @model_validator(mode="after")
    def _value_matches_feature(self) -> "CommunityAnswer":
        expected = COMMUNITY_FEATURE_VALUES[self.feature_key]
        if expected is bool and not isinstance(self.value, bool):
            raise ValueError(f"{self.feature_key.value} expects a true/false answer")
        if expected is DoorstepLevel and not isinstance(self.value, DoorstepLevel):
            allowed = ", ".join(level.value for level in DoorstepLevel)
            raise ValueError(f"{self.feature_key.value} expects one of: {allowed}")
        return self


class NewCommunityContribution(CommunityAnswer):
    place_id: str


class CommunityContribution(NewCommunityContribution):
    id: str
    submitted_at: datetime


class CommunityFeatureSummary(BaseModel):
    feature_key: CommunityFeatureKey
    total_responses: int = 0
    distribution: dict[str, int] = Field(default_factory=dict)
    top_value: bool | DoorstepLevel | None = None
    latest_value: bool | DoorstepLevel | None = None
    last_submitted_at: datetime | None = None


class CommunitySummary(BaseModel):
    place_id: str
    features: list[CommunityFeatureSummary]
