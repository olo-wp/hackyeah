-- RouteAble initial schema.
-- `evidence` is the source of truth; `accessibility_features` is a derived cache.

CREATE TABLE IF NOT EXISTS places (
    id           TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    category     TEXT NOT NULL,
    address      TEXT,
    latitude     DOUBLE PRECISION NOT NULL,
    longitude    DOUBLE PRECISION NOT NULL,
    external_ids JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS places_name_idx ON places (lower(name));

CREATE TABLE IF NOT EXISTS sources (
    id         TEXT PRIMARY KEY,
    type       TEXT NOT NULL,
    name       TEXT NOT NULL,
    url        TEXT,
    license    TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidence (
    id                  UUID PRIMARY KEY,
    place_id            TEXT NOT NULL REFERENCES places (id) ON DELETE CASCADE,
    source_id           TEXT NOT NULL REFERENCES sources (id) ON DELETE CASCADE,
    feature_key         TEXT NOT NULL,
    value               JSONB,
    source_url          TEXT,
    verification_status TEXT NOT NULL,
    retrieved_at        TIMESTAMPTZ NOT NULL,
    observed_at         TIMESTAMPTZ,
    raw_data            JSONB
);

CREATE INDEX IF NOT EXISTS evidence_place_feature_idx ON evidence (place_id, feature_key);

CREATE TABLE IF NOT EXISTS accessibility_features (
    id            UUID PRIMARY KEY,
    place_id      TEXT NOT NULL REFERENCES places (id) ON DELETE CASCADE,
    feature_key   TEXT NOT NULL,
    value         JSONB,
    status        TEXT NOT NULL,
    confidence    TEXT,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (place_id, feature_key)
);

CREATE TABLE IF NOT EXISTS place_provider_fetches (
    place_id   TEXT NOT NULL REFERENCES places (id) ON DELETE CASCADE,
    provider   TEXT NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (place_id, provider)
);

CREATE TABLE IF NOT EXISTS provider_syncs (
    id              UUID PRIMARY KEY,
    provider        TEXT NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ,
    status          TEXT NOT NULL,
    processed_items INTEGER NOT NULL DEFAULT 0,
    error           TEXT
);

CREATE TABLE IF NOT EXISTS user_reports (
    id                UUID PRIMARY KEY,
    place_id          TEXT NOT NULL REFERENCES places (id) ON DELETE CASCADE,
    feature_key       TEXT NOT NULL,
    issue_type        TEXT NOT NULL,
    message           TEXT NOT NULL,
    claimed_value     JSONB,
    moderation_status TEXT NOT NULL DEFAULT 'pending',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
