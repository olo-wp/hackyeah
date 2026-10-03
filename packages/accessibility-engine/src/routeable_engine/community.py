"""Aggregate anonymous community contributions into a per-feature summary."""

from collections import Counter

from routeable_model import (
    CommunityContribution,
    CommunityFeatureKey,
    CommunityFeatureSummary,
    CommunitySummary,
    DoorstepLevel,
)

# Answers older than this are dropped before aggregation (applied by the service).
COMMUNITY_FRESH_WINDOW_DAYS = 180


def _value_key(value: bool | DoorstepLevel) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return value.value


def _summarize_feature(
    feature_key: CommunityFeatureKey, contributions: list[CommunityContribution]
) -> CommunityFeatureSummary:
    if not contributions:
        return CommunityFeatureSummary(feature_key=feature_key)

    newest_first = sorted(contributions, key=lambda c: c.submitted_at, reverse=True)
    counts: Counter[str] = Counter(_value_key(c.value) for c in newest_first)
    ranked = counts.most_common()

    # A single most-common answer only; ties leave `top_value` unset.
    top_value: bool | DoorstepLevel | None = None
    if len(ranked) == 1 or ranked[0][1] > ranked[1][1]:
        winner = ranked[0][0]
        top_value = next(c.value for c in newest_first if _value_key(c.value) == winner)

    latest = newest_first[0]
    return CommunityFeatureSummary(
        feature_key=feature_key,
        total_responses=len(newest_first),
        distribution=dict(counts),
        top_value=top_value,
        latest_value=latest.value,
        last_submitted_at=latest.submitted_at,
    )


def summarize_contributions(
    place_id: str, contributions: list[CommunityContribution]
) -> CommunitySummary:
    grouped: dict[CommunityFeatureKey, list[CommunityContribution]] = {
        key: [] for key in CommunityFeatureKey
    }
    for contribution in contributions:
        grouped[contribution.feature_key].append(contribution)

    return CommunitySummary(
        place_id=place_id,
        features=[_summarize_feature(key, grouped[key]) for key in CommunityFeatureKey],
    )
