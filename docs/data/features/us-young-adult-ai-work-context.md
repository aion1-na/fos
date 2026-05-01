# Feature: us_young_adult_ai_work_context

Owner: Data Science

Version: `fixture-0.1`

Canonical dataset name: `features.us_young_adult_ai_work_context`

Inputs: RS-03 young-adult population output, occupation-group-to-SOC crosswalk, `features.occupation_ai_exposure_ensemble`, BLS OEWS, BLS LAUS, BLS QCEW, BLS Employment Projections, and CPS labor context.

Access and license metadata: source tables inherit their dataset-card access policies. Fixture-only unit-test rows cannot be promoted to production artifacts.

Codebook mapping: occupation groups map through `packages/data-pipelines/fixtures/ai_exposure/occupation_group_crosswalk_fixture_only.csv` in tests. Production runs require a versioned crosswalk with preserved source labels.

Quality profile: manifests record row count, minimum exposure-measure count among occupation-linked rows, and confirm `not_in_labor_force` rows do not receive fabricated occupation exposure, wage, or projection values.

Provenance manifest: each build emits `dataset_reference = (canonical_dataset_name, version, content_hash)` for the feature table and a `dataset_references` list for the population, crosswalk, exposure ensemble, wage, labor-market, projection, and CPS inputs.

Limitations: AI exposure scores are descriptive measurement inputs, not causal effect sizes. Missing or unavailable public archive sources remain request-status records until approved source bytes are registered.
