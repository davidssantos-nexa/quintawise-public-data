ALTER TABLE analyses ADD COLUMN IF NOT EXISTS name TEXT;
ALTER TABLE analyses ADD COLUMN IF NOT EXISTS snapshot JSONB;
CREATE INDEX IF NOT EXISTS analyses_created_at_idx ON analyses(created_at DESC);
