CREATE TABLE IF NOT EXISTS dataset_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    published_at DATE,
    downloaded_at TIMESTAMPTZ,
    checksum_sha256 TEXT,
    source_url TEXT,
    license TEXT,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    validation JSONB NOT NULL DEFAULT '{}'::jsonb,
    limitations JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO dataset_versions (
    dataset_id, version, published_at, downloaded_at, checksum_sha256,
    source_url, license, active, limitations
)
SELECT
    id, version, published_at, downloaded_at, checksum,
    source_url, license, active,
    CASE
        WHEN notes IS NULL THEN '[]'::jsonb
        ELSE jsonb_build_array(notes)
    END
FROM datasets
WHERE NOT EXISTS (
    SELECT 1 FROM dataset_versions v WHERE v.dataset_id = datasets.id
);

CREATE UNIQUE INDEX IF NOT EXISTS dataset_versions_identity_idx
ON dataset_versions (
    dataset_id,
    version,
    COALESCE(checksum_sha256, '')
);

CREATE UNIQUE INDEX IF NOT EXISTS dataset_versions_one_active_idx
ON dataset_versions (dataset_id)
WHERE active;

CREATE INDEX IF NOT EXISTS dataset_versions_dataset_created_idx
ON dataset_versions (dataset_id, created_at DESC);
