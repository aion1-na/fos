# Population Card: US Young Adult Flagship

Population id: `young-adult-calibrated`

Scope: 5,000 synthetic United States young adults ages 18-29 for the flourishing pack.

Synthesis method: IPF/raking over ACS, CPS, and GFS marginals using age, education, employment, household, income, geography, and occupation dimensions.

Required inputs: `acs_pums_young_adults`, `cps_young_adults`, and `gfs_wave12_panel_non_sensitive` dataset references. Demo runs may use fixture-only marginal bundles, but must set `demo_mode` and label outputs as fixture-only.

Export format: snapshot `agents.parquet`, `networks.parquet`, `institutions.parquet`, `fidelity.json`, and `manifest.json`, matching the current flourishing pack state fields and carrying `dataset_reference = (canonical_dataset_name, version, content_hash)`.

Diagnostics: `features.synthetic_population_calibration_diagnostics` reports max absolute standardized difference, KL divergence, marginal coverage, and target/observed shares for each calibrated dimension.

Imputation policy: childhood predictors and current context fields are filled from GFS distributions when available. Fields without approved distributions are generated from documented priors and listed under `imputation` in the snapshot manifest.

Restrictions: Do not fabricate production marginals. Fixture-only inputs are limited to tests and local demo runs.
