CREATE SCHEMA IF NOT EXISTS evidence_graph;

CREATE EXTENSION IF NOT EXISTS age;

SELECT create_graph('evidence_graph');

CREATE TABLE IF NOT EXISTS evidence_graph.claims (
  claim_id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  estimate DOUBLE PRECISION NOT NULL,
  uncertainty DOUBLE PRECISION NOT NULL,
  population TEXT NOT NULL,
  treatment TEXT NOT NULL,
  outcome TEXT NOT NULL,
  confidence_label TEXT NOT NULL,
  risk_of_bias TEXT NOT NULL,
  review_status TEXT NOT NULL,
  provenance_link TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_graph.citations (
  source_id TEXT PRIMARY KEY,
  canonical_dataset_name TEXT NOT NULL,
  access_status TEXT NOT NULL,
  dataset_card TEXT NOT NULL,
  provenance_manifest TEXT NOT NULL,
  citation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_graph.causal_edges (
  edge_id TEXT PRIMARY KEY,
  claim_id TEXT NOT NULL REFERENCES evidence_graph.claims (claim_id),
  treatment TEXT NOT NULL,
  outcome TEXT NOT NULL,
  direction TEXT NOT NULL
);
