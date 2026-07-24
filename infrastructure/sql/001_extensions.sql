CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    authority TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    license TEXT,
    geographic_scope TEXT,
    published_at DATE,
    downloaded_at TIMESTAMPTZ,
    version TEXT NOT NULL,
    checksum TEXT,
    active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    input_geometry geometry(Polygon, 4326) NOT NULL,
    metric_geometry geometry(Polygon, 3763) NOT NULL,
    area_m2 DOUBLE PRECISION NOT NULL,
    status TEXT NOT NULL DEFAULT 'completed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id),
    indicator TEXT NOT NULL,
    value_numeric DOUBLE PRECISION,
    value_text TEXT,
    unit TEXT,
    confidence TEXT NOT NULL,
    method TEXT NOT NULL,
    limitations JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
