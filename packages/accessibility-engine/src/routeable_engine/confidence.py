"""Deterministic confidence scoring (ARCHITECTURE section 17)."""

from datetime import UTC, datetime

from routeable_model import ConfidenceLevel, Evidence, SourceType, VerificationStatus

# MVP demonstration weights — not production values.
SOURCE_CONFIDENCE: dict[SourceType, float] = {
    SourceType.CITY_OPEN_DATA: 0.9,
    SourceType.OFFICIAL_WEBSITE: 0.9,
    SourceType.PARTNER_API: 0.9,
    SourceType.OPENSTREETMAP: 0.7,
    SourceType.USER_REPORT: 0.4,
    SourceType.DEMO_DATA: 0.3,
    SourceType.GOOGLE_SEARCH: 0.5,
}

HIGH_THRESHOLD = 0.8
MEDIUM_THRESHOLD = 0.55


def as_utc(value: datetime) -> datetime:
    """Treat naive timestamps as UTC so age arithmetic never raises."""
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def age_days(timestamp: datetime, now: datetime) -> float:
    return (as_utc(now) - as_utc(timestamp)).total_seconds() / 86_400


def freshness_modifier(retrieved_at: datetime, now: datetime) -> float:
    days = age_days(retrieved_at, now)
    if days < 30:
        return 1.0
    if days < 90:
        return 0.9
    if days < 365:
        return 0.75
    return 0.5


def score_evidence(evidence: Evidence, now: datetime) -> float:
    base = SOURCE_CONFIDENCE.get(evidence.source.type, 0.5)
    verification = 1.0 if evidence.verification_status == VerificationStatus.VERIFIED else 0.95
    return base * freshness_modifier(evidence.retrieved_at, now) * verification


def to_confidence_level(score: float) -> ConfidenceLevel:
    if score >= HIGH_THRESHOLD:
        return ConfidenceLevel.HIGH
    if score >= MEDIUM_THRESHOLD:
        return ConfidenceLevel.MEDIUM
    return ConfidenceLevel.LOW


def calculate_confidence(evidence: list[Evidence], now: datetime) -> ConfidenceLevel | None:
    """Agreeing independent sources raise confidence; a single stale source lowers it."""
    if not evidence:
        return None

    best = max(score_evidence(item, now) for item in evidence)
    independent_sources = len({item.source.id for item in evidence})
    bonus = 0.1 * (independent_sources - 1)

    return to_confidence_level(min(1.0, best + bonus))
