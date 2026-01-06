-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Works table - the main database of registered works
CREATE TABLE works (
    id SERIAL PRIMARY KEY,
    work_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    title_normalized VARCHAR(500) NOT NULL,
    alternative_titles TEXT[],
    iswc VARCHAR(20),
    songwriters TEXT[] NOT NULL,
    songwriters_normalized TEXT[] NOT NULL,
    publishers TEXT[],
    release_year INTEGER,
    genre VARCHAR(100),
    title_embedding vector(768),
    songwriter_embedding vector(768),
    combined_embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Usage records from uploaded files
CREATE TABLE usage_records (
    id SERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    recording_title VARCHAR(500),
    recording_artist VARCHAR(500),
    work_title VARCHAR(500),
    work_title_normalized VARCHAR(500),
    songwriter VARCHAR(500),
    songwriter_normalized VARCHAR(500),
    original_row_data JSONB,
    row_number INTEGER,
    title_embedding vector(768),
    songwriter_embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match results
CREATE TABLE match_results (
    id SERIAL PRIMARY KEY,
    usage_record_id INTEGER REFERENCES usage_records(id) ON DELETE CASCADE,
    work_id INTEGER REFERENCES works(id) ON DELETE CASCADE,
    confidence_score DECIMAL(5, 4) NOT NULL,
    match_type VARCHAR(50) NOT NULL, -- 'exact', 'high_confidence', 'medium_confidence', 'low_confidence', 'ai_matched'
    title_similarity DECIMAL(5, 4),
    songwriter_similarity DECIMAL(5, 4),
    vector_similarity DECIMAL(5, 4),
    ai_reasoning TEXT,
    is_confirmed BOOLEAN DEFAULT FALSE,
    is_rejected BOOLEAN DEFAULT FALSE,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Processing batches
CREATE TABLE processing_batches (
    id UUID PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    total_records INTEGER NOT NULL,
    processed_records INTEGER DEFAULT 0,
    matched_records INTEGER DEFAULT 0,
    unmatched_records INTEGER DEFAULT 0,
    flagged_records INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_works_title_normalized ON works(title_normalized);
CREATE INDEX idx_works_title_trgm ON works USING gin(title_normalized gin_trgm_ops);
CREATE INDEX idx_works_songwriters_trgm ON works USING gin(array_to_string(songwriters_normalized, ' ') gin_trgm_ops);
CREATE INDEX idx_works_title_embedding ON works USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_works_combined_embedding ON works USING ivfflat (combined_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_usage_batch ON usage_records(batch_id);
CREATE INDEX idx_usage_title_normalized ON usage_records(work_title_normalized);
CREATE INDEX idx_usage_title_embedding ON usage_records USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_match_usage ON match_results(usage_record_id);
CREATE INDEX idx_match_work ON match_results(work_id);
CREATE INDEX idx_match_confidence ON match_results(confidence_score);
CREATE INDEX idx_match_type ON match_results(match_type);

CREATE INDEX idx_batch_status ON processing_batches(status);

-- Function to normalize text for matching
CREATE OR REPLACE FUNCTION normalize_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(input_text, '[^\w\s]', '', 'g'),
            '\s+', ' ', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Trigger to auto-update normalized fields on works
CREATE OR REPLACE FUNCTION update_works_normalized()
RETURNS TRIGGER AS $$
BEGIN
    NEW.title_normalized := normalize_text(NEW.title);
    NEW.songwriters_normalized := ARRAY(
        SELECT normalize_text(unnest) FROM unnest(NEW.songwriters)
    );
    NEW.updated_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER works_normalize_trigger
    BEFORE INSERT OR UPDATE ON works
    FOR EACH ROW
    EXECUTE FUNCTION update_works_normalized();

-- Trigger to auto-update normalized fields on usage_records
CREATE OR REPLACE FUNCTION update_usage_normalized()
RETURNS TRIGGER AS $$
BEGIN
    NEW.work_title_normalized := normalize_text(COALESCE(NEW.work_title, NEW.recording_title));
    NEW.songwriter_normalized := normalize_text(COALESCE(NEW.songwriter, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER usage_normalize_trigger
    BEFORE INSERT OR UPDATE ON usage_records
    FOR EACH ROW
    EXECUTE FUNCTION update_usage_normalized();
