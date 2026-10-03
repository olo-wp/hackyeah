"""Evidence — every fact keeps a link back to the source it came from."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .features import FeatureKey
from .source import DataSource


class VerificationStatus(StrEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    SELF_REPORTED = "self_reported"
    AUTOMATICALLY_EXTRACTED = "automatically_extracted"


class Evidence(BaseModel):
    id: str
    place_id: str
    feature_key: FeatureKey
    source: DataSource
    value: Any = None
    retrieved_at: datetime = Field(description="When RouteAble fetched the data")
    observed_at: datetime | None = Field(
        default=None, description="When the fact was observed in the real world, if known"
    )
    verification_status: VerificationStatus
    raw_data: Any | None = None


class RawAccessibilityEvidence(BaseModel):
    """What a provider returns, before it is given an id and a persisted source."""

    feature_key: FeatureKey
    value: Any = None
    observed_at: datetime | None = None
    verification_status: VerificationStatus
    raw_data: Any | None = None
    source_url: str | None = Field(
        default=None, description="Deep link to the exact page or dataset entry"
    )
