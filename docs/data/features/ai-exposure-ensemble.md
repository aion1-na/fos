# Feature: ai_exposure_ensemble

Owner: Data Science

Version: `0.1`

Inputs: Eloundou fixture, Felten fixture, Webb request-status fixture, Anthropic Economic Index request-status fixture, SOC/O*NET/Census crosswalk v0.1.

Rule: headline outputs require at least two exposure measures. Single-measure outputs are rejected.

Uncertainty metadata:

- `measure_count`
- `mean_exposure`
- `min_exposure`
- `max_exposure`
- `range_disagreement`
- `standard_deviation`
- `disagreement_level`

Simulation-facing outputs must include `dataset_reference = (canonical_dataset_name, version, content_hash)`.
