# Dataset Card: GFS Wave 1

Canonical dataset name: `gfs_wave1`

Version: `request-status-v0.1` until approved production bytes are registered; fixture-only tests use `fixture-0.1`.

Access status: non-sensitive Wave 1 microdata is registration-gated through the approved GFS COS/OSF portal workflow. The connector detects approved local/controlled bytes when supplied and otherwise emits request-status metadata with no rows.

License metadata: registration-gated; no production license grant is stored in source control.

Sampling design: Wave 1 survey with respondent-level sampling weights. Test fixtures are named `fixture_only` and are not production-facing data.

Weights: `weight` is required for country marginals, the 10-item Flourish index, and the 12-item Secure Flourish index.

Limitations: research-grade measurement only. Sensitive variables are blocked unless an approved access policy is present. This card does not authorize prospective forecasting or causal effect-size claims.

Citation instructions: cite the official GFS Wave 1 methodology and portal/OSF record once access is approved; fixture outputs cite this repository fixture only.

Codebook mapping: `codebooks/gfs_wave1.yaml`

Quality profile: connector tests enforce non-sensitive field splits, source label preservation, request-status fallback, content hashes, and weighted scoring checks against fixture-only reference outputs.

Provenance manifest: content hash computed from approved source bytes or request-status metadata.

Access policy: no sensitive production reads until registration, license metadata, and explicit sensitive-data approval are recorded.

Simulation output status: feature outputs must include `dataset_reference = (canonical_dataset_name, version, content_hash)`.
