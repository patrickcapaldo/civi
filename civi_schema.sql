-- CIVI PostgreSQL Schema
-- This script creates the tables for the Critical Infrastructure Vitals Index.

-- Turn off notices for cleaner output
SET client_min_messages TO WARNING;

-- Drop existing tables in reverse order of dependency to avoid foreign key constraint errors
DROP TABLE IF EXISTS etl_runs, normalization_log, country_scores, industry_scores, pillar_scores, metrics_normalized, metrics_raw, metrics_catalog;

-- =============================================
-- Table: metrics_catalog
-- Description: Stores metadata for all metrics.
-- =============================================
CREATE TABLE metrics_catalog (
    metric_id VARCHAR(100) PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    industry VARCHAR(50) NOT NULL,
    pillar VARCHAR(50) NOT NULL,
    units VARCHAR(50),
    directionality CHAR(3) CHECK (directionality IN ('POS', 'NEG')), -- POS for positive, NEG for negative
    source TEXT,
    source_url TEXT,
    coverage_notes TEXT
);

COMMENT ON TABLE metrics_catalog IS 'Metadata for all metrics: name, description, industry, pillar, units, directionality, source, etc.';
COMMENT ON COLUMN metrics_catalog.directionality IS 'POS = higher is better, NEG = lower is better';

-- =============================================
-- Table: metrics_raw
-- Description: Stores raw metric values as fetched from source.
-- =============================================
CREATE TABLE metrics_raw (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    metric_id VARCHAR(100) NOT NULL REFERENCES metrics_catalog(metric_id),
    metric_value DOUBLE PRECISION,
    units VARCHAR(50),
    source TEXT,
    fetched_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(country_code, year, metric_id)
);

CREATE INDEX idx_metrics_raw_country_year ON metrics_raw (country_code, year);
COMMENT ON TABLE metrics_raw IS 'Raw source values for each metric, country, and year.';

-- =============================================
-- Table: metrics_normalized
-- Description: Stores normalized metric values (0-100 scale).
-- =============================================
CREATE TABLE metrics_normalized (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    metric_id VARCHAR(100) NOT NULL REFERENCES metrics_catalog(metric_id),
    normalized_value DOUBLE PRECISION,
    normalization_method VARCHAR(50),
    normalization_window VARCHAR(50), -- e.g., 'global', '2000-2020'
    CONSTRAINT value_in_range CHECK (normalized_value >= 0 AND normalized_value <= 100),
    UNIQUE(country_code, year, metric_id)
);

CREATE INDEX idx_metrics_normalized_country_year ON metrics_normalized (country_code, year);
COMMENT ON TABLE metrics_normalized IS 'Normalized metric values on a 0-100 scale.';

-- =============================================
-- Table: pillar_scores
-- Description: Aggregated scores per country-year-industry-pillar.
-- =============================================
CREATE TABLE pillar_scores (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    industry VARCHAR(50) NOT NULL,
    pillar VARCHAR(50) NOT NULL,
    pillar_score DOUBLE PRECISION,
    UNIQUE(country_code, year, industry, pillar)
);

CREATE INDEX idx_pillar_scores_country_year ON pillar_scores (country_code, year);
COMMENT ON TABLE pillar_scores IS 'Aggregated scores for each pillar within an industry.';

-- =============================================
-- Table: industry_scores
-- Description: Aggregated scores per country-year-industry.
-- =============================================
CREATE TABLE industry_scores (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    industry VARCHAR(50) NOT NULL,
    industry_score DOUBLE PRECISION,
    UNIQUE(country_code, year, industry)
);

CREATE INDEX idx_industry_scores_country_year ON industry_scores (country_code, year);
COMMENT ON TABLE industry_scores IS 'Aggregated scores for each industry.';

-- =============================================
-- Table: country_scores
-- Description: Final aggregated CIVI score per country-year.
-- =============================================
CREATE TABLE country_scores (
    id BIGSERIAL PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    country_score DOUBLE PRECISION,
    UNIQUE(country_code, year)
);

CREATE INDEX idx_country_scores_year ON country_scores (year);
COMMENT ON TABLE country_scores IS 'Overall aggregated CIVI score for each country.';

-- =============================================
-- Table: normalization_log
-- Description: Logs parameters used during normalization for reproducibility.
-- =============================================
CREATE TABLE normalization_log (
    id BIGSERIAL PRIMARY KEY,
    metric_id VARCHAR(100) NOT NULL REFERENCES metrics_catalog(metric_id),
    run_id VARCHAR(100),
    normalization_method VARCHAR(50),
    window_start_year INT,
    window_end_year INT,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    log_timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE normalization_log IS 'Stores min/max values and methods used for normalization reproducibility.';

-- =============================================
-- Table: etl_runs
-- Description: Tracks ETL/data refresh jobs.
-- =============================================
CREATE TABLE etl_runs (
    id BIGSERIAL PRIMARY KEY,
    source VARCHAR(100),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    status VARCHAR(20) CHECK (status IN ('success', 'failure', 'running')),
    records_processed INT,
    notes TEXT
);

COMMENT ON TABLE etl_runs IS 'Tracks the status and metadata of ETL/data refresh runs.';

-- =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
-- Example Data Insertion (for demonstration)
-- =_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=_=
-- This section can be commented out in production.

-- 1. Populate the metric catalog
INSERT INTO metrics_catalog (metric_id, name, industry, pillar, directionality, source, units) VALUES
('WB_IT_NET_USER_P2', 'Individuals using the Internet (% of population)', 'Information Technology', 'Effectiveness', 'POS', 'World Bank', '%'),
('WB_EG_ELC_ACCS_ZS', 'Access to electricity (% of population)', 'Energy', 'Effectiveness', 'POS', 'World Bank', '%'),
('FAO_FS_DEFI_P3', 'Prevalence of undernourishment (% of population)', 'Food & Agriculture', 'Resilience', 'NEG', 'FAOSTAT', '%');

-- 2. Insert some raw data
INSERT INTO metrics_raw (country_code, year, metric_id, metric_value) VALUES
('USA', 2020, 'WB_IT_NET_USER_P2', 90.0),
('CHN', 2020, 'WB_IT_NET_USER_P2', 70.0),
('USA', 2020, 'WB_EG_ELC_ACCS_ZS', 100.0),
('SSD', 2020, 'WB_EG_ELC_ACCS_ZS', 7.2);

-- End of Schema
