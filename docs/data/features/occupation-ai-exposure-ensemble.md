# Feature: occupation_ai_exposure_ensemble

Owner: Data Science

Version: `fixture-0.1`

Canonical dataset name: `features.occupation_ai_exposure_ensemble`

Inputs: Eloundou fixture-only parser, Felten fixture-only parser, Acemoglu/Restrepo robot fixture-only parser, Webb request-status stub, Anthropic Economic Index request-status stub, and SOC/O*NET/Census crosswalk v0.1.

Rule: headline outputs require at least two exposure measures. Single-measure outputs are rejected.

Uncertainty metadata:

- `measure_count`
- `measure_names`
- `measure_versions`
- `mean_exposure`
- `min_exposure`
- `max_exposure`
- `range_disagreement`
- `standard_deviation`
- `disagreement_level`
- `uncertainty_signal`

Demographic subgroup reporting: `features.occupation_ai_demographic_distributions` carries the ensemble disagreement fields by occupation, geography, and demographic group. It is an uncertainty view, not a causal effect estimate.

License metadata: source-specific terms remain pending for production. Fixture-only rows are unit-test artifacts and cannot be used for production claims.

Quality profile: tests reject single-measure headline outputs, require dataset references on feature rows, and verify demographic-subgroup disagreement metadata.

Provenance manifest: feature content hash is computed from all approved input bytes and stored in `dataset_reference = (canonical_dataset_name, version, content_hash)`.

Access policy: request-status sources cannot be read into feature tables until their public archive or access terms are approved.
