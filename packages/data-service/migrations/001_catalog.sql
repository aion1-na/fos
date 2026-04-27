CREATE TABLE IF NOT EXISTS connector_versions (
  connector_name TEXT NOT NULL,
  connector_version TEXT NOT NULL,
  registered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (connector_name, connector_version)
);

CREATE TABLE IF NOT EXISTS dataset_versions (
  canonical_dataset_name TEXT NOT NULL,
  dataset_version TEXT NOT NULL,
  access_status TEXT NOT NULL,
  registered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (canonical_dataset_name, dataset_version)
);

CREATE TABLE IF NOT EXISTS artifacts (
  artifact_id TEXT PRIMARY KEY,
  canonical_dataset_name TEXT NOT NULL,
  dataset_version TEXT NOT NULL,
  connector_name TEXT NOT NULL,
  connector_version TEXT NOT NULL,
  artifact_kind TEXT NOT NULL,
  artifact_uri TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  FOREIGN KEY (canonical_dataset_name, dataset_version)
    REFERENCES dataset_versions (canonical_dataset_name, dataset_version),
  FOREIGN KEY (connector_name, connector_version)
    REFERENCES connector_versions (connector_name, connector_version)
);

CREATE INDEX IF NOT EXISTS artifacts_dataset_connector_idx
  ON artifacts (canonical_dataset_name, dataset_version, connector_name, connector_version);
