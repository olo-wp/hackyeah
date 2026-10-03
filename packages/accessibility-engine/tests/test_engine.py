from datetime import UTC, datetime, timedelta
from typing import Any

from routeable_engine import build_accessibility_profile, resolve_feature
from routeable_model import (
    DataSource,
    Evidence,
    FeatureKey,
    FeatureStatus,
    SourceType,
    VerificationStatus,
)

NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)

OSM = DataSource(id="osm", type=SourceType.OPENSTREETMAP, name="OpenStreetMap")
WEBSITE = DataSource(id="website", type=SourceType.OFFICIAL_WEBSITE, name="Official website")


def evidence(
    feature_key: FeatureKey,
    value: Any,
    source: DataSource = OSM,
    retrieved_at: datetime = NOW,
) -> Evidence:
    return Evidence(
        id=f"{source.id}-{feature_key}",
        place_id="osm:node:1",
        feature_key=feature_key,
        source=source,
        value=value,
        retrieved_at=retrieved_at,
        verification_status=VerificationStatus.UNVERIFIED,
    )


def test_missing_data_stays_unknown() -> None:
    feature = resolve_feature(FeatureKey.ELEVATOR, [], NOW)

    assert feature.status == FeatureStatus.UNKNOWN
    assert feature.value is None
    assert feature.confidence is None


def test_agreeing_sources_raise_confidence() -> None:
    feature = resolve_feature(
        FeatureKey.ELEVATOR,
        [
            evidence(FeatureKey.ELEVATOR, True, OSM),
            evidence(FeatureKey.ELEVATOR, True, WEBSITE),
        ],
        NOW,
    )

    assert feature.status == FeatureStatus.CONFIRMED
    assert feature.value is True
    assert feature.confidence == "high"


def test_disagreeing_sources_conflict() -> None:
    feature = resolve_feature(
        FeatureKey.ELEVATOR,
        [
            evidence(FeatureKey.ELEVATOR, True, OSM),
            evidence(FeatureKey.ELEVATOR, False, WEBSITE),
        ],
        NOW,
    )

    assert feature.status == FeatureStatus.CONFLICTING
    assert feature.value is None
    assert len(feature.evidence) == 2


def test_old_evidence_is_stale() -> None:
    feature = resolve_feature(
        FeatureKey.ELEVATOR,
        [evidence(FeatureKey.ELEVATOR, True, OSM, NOW - timedelta(days=400))],
        NOW,
    )

    assert feature.status == FeatureStatus.STALE


def test_step_free_claim_conflicts_with_reported_steps() -> None:
    profile = build_accessibility_profile(
        "osm:node:1",
        [
            evidence(FeatureKey.STEP_FREE_ENTRANCE, True, OSM),
            evidence(FeatureKey.ENTRANCE_STEPS, 3, WEBSITE),
        ],
        NOW,
    )

    assert profile.entrance.step_free.status == FeatureStatus.CONFLICTING
    assert profile.entrance.steps.status == FeatureStatus.CONFLICTING
    assert profile.metadata.source_count == 2
