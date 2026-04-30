# Dataset Card: GFS Wave 1/2 Country Marginal Features

Canonical dataset name pattern: `features.gfs_wave12_marginals_country_*`

Version: `request-status-v0.1` for production-facing registration-gated data; fixture-only tests use `fixture-0.1`.

Access status: derived from `features.gfs_wave12_panel_non_sensitive`; no direct sensitive or raw microdata access is exposed.

License metadata: inherits GFS Wave 1/2 registration-gated license terms; no production license grant is stored in source control.

Weights: country marginals are respondent-weighted using `sampling_weight`.

Limitations: descriptive country aggregates for research validation only. They are not causal effect sizes and do not authorize prospective forecasting.

Citation instructions: cite the official GFS Wave 1 and Wave 2 methodology and portal/OSF records once access is approved; fixture-only outputs cite repository fixtures only.

Codebook mapping: `codebooks/gfs_wave1.yaml`, `codebooks/gfs_wave2.yaml`, and the derived measure names documented in `fos_data_pipelines.scoring.flourishing`.

Quality profile: tests enforce weighted country aggregates, emitted measure coverage, and complete `dataset_reference` tuples.

Provenance manifest: each country feature `content_hash` is computed from emitted country marginal rows before `dataset_reference` injection.

Access policy: no raw or sensitive fields are included in country marginal outputs.

Simulation output status: feature outputs include `dataset_reference = (canonical_dataset_name, version, content_hash)`.
