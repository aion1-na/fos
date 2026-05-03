# Dataset Card: Felten AI Exposure

Canonical dataset name: `felten_ai_exposure`

Version: `fixture-0.1`

Access status: fixture-only parser for unit tests; production use requires source review

License metadata: request-status stub for production terms; do not promote fixture-only rows to production artifacts

Codebook mapping: `codebooks/ai_exposure_measures.yaml`

Quality profile: fixture-only parse validates measure count, source occupation code coverage, and staged Parquet readability

Provenance manifest: fixture-only content hash computed during tests

Access policy: no live reads except approved smoke-test command

Simulation output status: only `features.occupation_ai_exposure_ensemble` may expose simulation-facing rows, and every row must include `dataset_reference`.
