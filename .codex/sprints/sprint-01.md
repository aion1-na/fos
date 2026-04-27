# Sprint 01: Raw Landing and Connector Contract

Objective: build raw landing discipline and a reusable Connector contract before dataset work becomes ad hoc.

## Deliverables

- Pydantic `ConnectorConfig` and artifact models.
- S3/MinIO raw zone abstraction.
- Postgres catalog migrations.
- Dagster asset skeleton.
- `RawArtifact`, `StagedArtifact`, `HarmonizedArtifact`, and `FeatureTable` schemas.
- Unit tests with fixture artifacts and hash determinism.

## Acceptance Gates

- Same raw file lands to the same hash path twice.
- Connector versions are registered separately from dataset versions.
- Catalog can answer: what data version and connector version produced this artifact?
- No platform code reads raw files directly.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved endpoints or credentials.
