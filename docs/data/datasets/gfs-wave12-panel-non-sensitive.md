# Dataset Card: GFS Wave 1/2 Non-Sensitive Panel Features

Canonical dataset name: `features.gfs_wave12_panel_non_sensitive`

Version: `request-status-v0.1` for production-facing registration-gated data; fixture-only tests use `fixture-0.1`.

Access status: derived only from approved GFS Wave 1/2 non-sensitive source bytes or request-status metadata. Sensitive fields are blocked before feature construction.

License metadata: inherits GFS Wave 1/2 registration-gated license terms; no production license grant is stored in source control.

Weights: uses respondent `weight` as `sampling_weight` for longitudinal feature rows.

Limitations: research-grade longitudinal measurement table only. It is not a causal estimate and must not be used for prospective forecasting claims without separate validation.

Citation instructions: cite the official GFS Wave 1 and Wave 2 methodology and portal/OSF records once access is approved; fixture-only outputs cite repository fixtures only.

Codebook mapping: `codebooks/gfs_wave1.yaml` and `codebooks/gfs_wave2.yaml`

Quality profile: tests enforce non-sensitive field splits, 10-item/12-item scoring, stable content hashes, and complete `dataset_reference` tuples.

Provenance manifest: feature `content_hash` is computed from emitted non-sensitive feature rows before `dataset_reference` injection.

Access policy: no sensitive variables may enter this feature table without explicit approved sensitive-data policy.

Simulation output status: feature outputs include `dataset_reference = (canonical_dataset_name, version, content_hash)`.
