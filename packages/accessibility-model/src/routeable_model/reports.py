"""User reports and provider sync bookkeeping."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from .features import FeatureKey


class ReportIssueType(StrEnum):
    INCORRECT_INFORMATION = "incorrect_information"
    OUTDATED_INFORMATION = "outdated_information"
    MISSING_INFORMATION = "missing_information"
    CONFLICTING_INFORMATION = "conflicting_information"


class ModerationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class NewAccessibilityReport(BaseModel):
    place_id: str
    feature_key: FeatureKey
    issue_type: ReportIssueType
    message: str = Field(min_length=5, max_length=1000)
    claimed_value: Any = None


class AccessibilityReport(NewAccessibilityReport):
    id: str
    created_at: datetime
    moderation_status: ModerationStatus = ModerationStatus.PENDING


class SyncStatus(StrEnum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class ProviderSync(BaseModel):
    provider: str
    started_at: datetime
    finished_at: datetime | None = None
    status: SyncStatus
    processed_items: int = 0
    error: str | None = None
