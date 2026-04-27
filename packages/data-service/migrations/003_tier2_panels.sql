CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE SCHEMA IF NOT EXISTS tier2;

CREATE TABLE IF NOT EXISTS tier2.access_requests (
  canonical_dataset_name TEXT PRIMARY KEY,
  owner TEXT NOT NULL,
  submitted_on DATE,
  access_status TEXT NOT NULL,
  license_status TEXT NOT NULL,
  secure_compartment TEXT NOT NULL,
  requested_use TEXT NOT NULL,
  updated_on DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS tier2.longitudinal_panel (
  person_id TEXT NOT NULL,
  household_id TEXT NOT NULL,
  wave INTEGER NOT NULL,
  observed_at TIMESTAMPTZ NOT NULL,
  country TEXT NOT NULL,
  weights JSONB NOT NULL,
  outcomes JSONB NOT NULL,
  treatments JSONB NOT NULL,
  attrition_metadata JSONB NOT NULL,
  dataset_reference JSONB NOT NULL,
  PRIMARY KEY (person_id, wave, observed_at)
);

SELECT create_hypertable('tier2.longitudinal_panel', 'observed_at', if_not_exists => TRUE);

CREATE MATERIALIZED VIEW IF NOT EXISTS tier2.panel_person_wave AS
SELECT person_id, wave, country, weights, outcomes, treatments, attrition_metadata, dataset_reference
FROM tier2.longitudinal_panel;

CREATE MATERIALIZED VIEW IF NOT EXISTS tier2.panel_wave_summary AS
SELECT country, wave, count(*) AS person_wave_count
FROM tier2.longitudinal_panel
GROUP BY country, wave;
