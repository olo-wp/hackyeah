-- Anonymous, uncertain community answers — kept apart from the certain `evidence` table.

CREATE TABLE IF NOT EXISTS community_contributions (
    id           UUID PRIMARY KEY,
    place_id     TEXT NOT NULL REFERENCES places (id) ON DELETE CASCADE,
    feature_key  TEXT NOT NULL,
    value        JSONB NOT NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS community_contributions_place_feature_idx
    ON community_contributions (place_id, feature_key, submitted_at DESC);
