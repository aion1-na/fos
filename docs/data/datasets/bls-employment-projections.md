# Dataset Card: BLS Employment Projections

Canonical dataset name: `bls_employment_projections`

Version: `request-status-v0.1`

Access status: request-status stub; fixture-only parser available for tests

License metadata: public BLS source, pending production-use review

Codebook mapping: `codebooks/bls_employment_projections.yaml`

Quality profile: fixture-only tests validate staged Parquet readability and required occupation projection fields

Provenance manifest: content hash computed from landed fixture-only source during tests

Access policy: no live calls except approved public endpoint smoke-test command

Simulation output status: simulation-facing derivatives must include `dataset_reference`.
