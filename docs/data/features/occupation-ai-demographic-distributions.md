# Feature: occupation_ai_demographic_distributions

Owner: Data Science

Version: `fixture-0.1`

Canonical dataset name: `features.occupation_ai_demographic_distributions`

Inputs: `features.occupation_ai_exposure_ensemble` and occupation demographic distribution tables.

Access and license metadata: inherits source access policies from the ensemble and demographic aggregate source. Fixture-only rows are restricted to unit tests.

Codebook mapping: occupation codes use the same source occupation code carried by the ensemble.

Quality profile: rows carry `measure_count`, `range_disagreement`, `standard_deviation`, `disagreement_level`, and `uncertainty_signal` by occupation, demographic group, and geography. Single-score headlines remain disallowed.

Provenance manifest: output rows include `dataset_reference = (canonical_dataset_name, version, content_hash)` computed from the ensemble table and demographic aggregate input bytes.

Limitations: subgroup disagreement is descriptive uncertainty metadata. It is not a causal effect size and must not be interpreted as model validation for any subgroup.
