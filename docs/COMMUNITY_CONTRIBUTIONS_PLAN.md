# Community Contributions — Implementation Plan

Anonymous, crowd-sourced accessibility answers for a place. Most questions are yes/no
(e.g. accessible parking); the doorstep question is 3-way (none / small / high).

This data is **uncertain** and is kept **completely separate** from the certain `evidence`
table and from provider profile resolution. It is informational only and is never merged
into the resolved `AccessibilityProfile`.

## Decisions

- **Storage:** one append-only row per answer (`place_id`, `feature_key`, `value`,
  `submitted_at`), aggregated on read. Mirrors the existing append-only `evidence` pattern;
  a counter is derivable from rows, not the other way around.
- **Anonymity:** no user identity is stored — no account, no client token. Spam is limited
  only by the existing app-level rate limiter.
- **Freshness:** aggregation counts only answers from the last 180 days
  (`COMMUNITY_FRESH_WINDOW_DAYS`), reusing the engine's stale window.
- **Feature set:** `accessible_parking`, `accessible_toilet`, `step_free_entrance`, `ramp`,
  `elevator` (boolean) and `doorstep` (none/small/high).

## Data model

New table `community_contributions`:

| column        | type          | notes                                   |
| ------------- | ------------- | --------------------------------------- |
| `id`          | `UUID` PK     |                                         |
| `place_id`    | `TEXT`        | FK → `places(id)` `ON DELETE CASCADE`   |
| `feature_key` | `TEXT`        | a `CommunityFeatureKey` value           |
| `value`       | `JSONB`       | boolean, or a `DoorstepLevel` string    |
| `submitted_at`| `TIMESTAMPTZ` | defaults to `now()`                     |

Index on `(place_id, feature_key, submitted_at DESC)`.

## Layers

- **Model** (`routeable_model.community`): `DoorstepLevel`, `CommunityFeatureKey`,
  `COMMUNITY_FEATURE_VALUES`, `CommunityAnswer` (feature_key + value + per-feature value-type
  validator), `NewCommunityContribution` (adds `place_id`), `CommunityContribution`
  (adds `id`, `submitted_at`), `CommunityFeatureSummary`, `CommunitySummary`.
- **Engine** (`routeable_engine.community`): `COMMUNITY_FRESH_WINDOW_DAYS` and
  `summarize_contributions(place_id, contributions)` — per-feature distribution, `top_value`
  (unset on ties), latest value, and a summary row for every feature.
- **Store**: `add_community_contribution` and
  `get_community_contributions(place_id, feature_key=None, since=None)` on the `EvidenceStore`
  protocol, the in-memory store, and the Postgres store.
- **Service**: `submit_community_contribution` (404 if the place is unknown) and
  `get_community_summary` (applies the 180-day window).
- **API** (`/api/places/{place_id}/community`): `POST` (202) a `CommunityAnswer`, `GET` the
  `CommunitySummary`. Invalid value-for-feature → 422; unknown place → 404.
- **Web**: a `CommunityContributions` client component on the place page with accessible
  radio groups, live counts and an `aria-live` status, submitting via a server action that
  revalidates the page. Copy added to the `pl` and `en` dictionaries.

## Tests

- Engine: distribution, tie → no `top_value`, latest selection, every feature present.
- API: boolean 202, doorstep 202, wrong value type 422, unknown place 404, summary counts.

## Out of scope

Moderation/admin UI, auth, editing or deleting your own answer, client-token dedup, merging
community answers into provider evidence or the resolved profile, map UI, MCP changes.
