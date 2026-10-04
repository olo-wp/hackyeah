from datetime import UTC, datetime, timedelta

from routeable_engine import summarize_contributions
from routeable_model import (
    CommunityContribution,
    CommunityFeatureSummary,
    CommunitySummary,
    FeatureKey,
)

NOW = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)


def contribution(
    feature_key: FeatureKey,
    value: bool | str,
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


def _feature(summary: CommunitySummary, key: FeatureKey) -> CommunityFeatureSummary:
    return next(f for f in summary.features if f.feature_key == key)


def test_empty_summary_lists_every_feature() -> None:
    summary = summarize_contributions("krakow:test", [])

    assert {f.feature_key for f in summary.features} == set(FeatureKey)
    for feature in summary.features:
        assert feature.total_responses == 0
        assert feature.distribution == {}
        assert feature.top_value is None
        assert feature.last_submitted_at is None


def test_distribution_and_top_value() -> None:
    summary = summarize_contributions(
        "krakow:test",
        [
            contribution(FeatureKey.THRESHOLD_CM, "small", NOW, "1"),
            contribution(FeatureKey.THRESHOLD_CM, "small", NOW - timedelta(days=1), "2"),
            contribution(FeatureKey.THRESHOLD_CM, "high", NOW - timedelta(days=2), "3"),
        ],
    )

    threshold = _feature(summary, FeatureKey.THRESHOLD_CM)
    assert threshold.total_responses == 3
    assert threshold.distribution == {"small": 2, "high": 1}
    assert threshold.top_value == "small"
    assert threshold.latest_value == "small"
    assert threshold.last_submitted_at == NOW


def test_tie_leaves_top_value_unset() -> None:
    summary = summarize_contributions(
        "krakow:test",
        [
            contribution(FeatureKey.ACCESSIBLE_PARKING, True, NOW, "1"),
            contribution(FeatureKey.ACCESSIBLE_PARKING, False, NOW - timedelta(days=1), "2"),
        ],
    )

    parking = _feature(summary, FeatureKey.ACCESSIBLE_PARKING)
    assert parking.total_responses == 2
    assert parking.distribution == {"true": 1, "false": 1}
    assert parking.top_value is None
    assert parking.latest_value is True
