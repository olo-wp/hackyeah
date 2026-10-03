from datetime import UTC, datetime, timedelta

from routeable_engine import summarize_contributions
from routeable_model import (
    CommunityContribution,
    CommunityFeatureKey,
    CommunityFeatureSummary,
    CommunitySummary,
    DoorstepLevel,
)

NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)


def contribution(
    feature_key: CommunityFeatureKey,
    value: bool | DoorstepLevel,
    submitted_at: datetime = NOW,
    id: str = "c",
) -> CommunityContribution:
    return CommunityContribution(
        id=id,
        place_id="krakow:test",
        feature_key=feature_key,
        value=value,
        submitted_at=submitted_at,
    )


def _feature(summary: CommunitySummary, key: CommunityFeatureKey) -> CommunityFeatureSummary:
    return next(f for f in summary.features if f.feature_key == key)


def test_empty_summary_lists_every_feature() -> None:
    summary = summarize_contributions("krakow:test", [])

    assert {f.feature_key for f in summary.features} == set(CommunityFeatureKey)
    for feature in summary.features:
        assert feature.total_responses == 0
        assert feature.distribution == {}
        assert feature.top_value is None
        assert feature.last_submitted_at is None


def test_distribution_and_top_value() -> None:
    summary = summarize_contributions(
        "krakow:test",
        [
            contribution(CommunityFeatureKey.DOORSTEP, DoorstepLevel.SMALL, NOW, "1"),
            contribution(
                CommunityFeatureKey.DOORSTEP, DoorstepLevel.SMALL, NOW - timedelta(days=1), "2"
            ),
            contribution(
                CommunityFeatureKey.DOORSTEP, DoorstepLevel.HIGH, NOW - timedelta(days=2), "3"
            ),
        ],
    )

    doorstep = _feature(summary, CommunityFeatureKey.DOORSTEP)
    assert doorstep.total_responses == 3
    assert doorstep.distribution == {"small": 2, "high": 1}
    assert doorstep.top_value == DoorstepLevel.SMALL
    assert doorstep.latest_value == DoorstepLevel.SMALL
    assert doorstep.last_submitted_at == NOW


def test_tie_leaves_top_value_unset() -> None:
    summary = summarize_contributions(
        "krakow:test",
        [
            contribution(CommunityFeatureKey.ACCESSIBLE_PARKING, True, NOW, "1"),
            contribution(
                CommunityFeatureKey.ACCESSIBLE_PARKING, False, NOW - timedelta(days=1), "2"
            ),
        ],
    )

    parking = _feature(summary, CommunityFeatureKey.ACCESSIBLE_PARKING)
    assert parking.total_responses == 2
    assert parking.distribution == {"true": 1, "false": 1}
    assert parking.top_value is None
    assert parking.latest_value is True
