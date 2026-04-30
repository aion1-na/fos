# Dataset Card: US Young Adult Population Marginals

Canonical dataset name: `features.us_young_adult_population_marginals`

Version: `request-status-v0.1`

Access status: derived feature table; production generation requires approved ACS PUMS, CPS, and GFS dataset references

License metadata: inherits ACS PUMS, CPS, and GFS license/access metadata

Codebook mapping: `docs/data/crosswalks/us-young-adult-population-v0.1.md`

Quality profile: marginal totals must be positive; age, education, employment, household, income, geography, and occupation dimensions must all be present; calibration diagnostics must report max absolute standardized difference, KL divergence, and marginal coverage

Provenance manifest: population snapshot manifests include the marginal bundle path, source dataset references, demo-mode flag, and content hash

Access policy: the generator refuses to run without ACS, CPS, and GFS references unless `demo_mode` is explicit

Simulation output status: exported snapshots include `dataset_reference = (canonical_dataset_name, version, content_hash)`.
