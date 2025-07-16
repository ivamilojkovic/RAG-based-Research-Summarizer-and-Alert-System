alerts_schema = """
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY,
    query TEXT NOT NULL,
    period INTEGER NOT NULL,
    status TEXT NOT NULL,
    summary JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
"""
papers_schema = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS papers (
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id TEXT NOT NULL,
    source TEXT NOT NULL,
    title TEXT,
    summary TEXT,
    link TEXT,
    published TIMESTAMP,
    updated TIMESTAMP,
    authors TEXT[],
    categories TEXT[],
    UNIQUE(source, source_id)
);
"""