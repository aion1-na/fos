# Sprint 03: AI Exposure Ensemble and Disagreement

Objective: implement mandatory ensemble exposure scoring and expose disagreement as a first-class uncertainty signal.

## Deliverables

- Connectors for Felten, Webb, and Anthropic Economic Index.
- Versioned SOC/O*NET/Census occupation crosswalks.
- `features.ai_exposure_ensemble` and `features.occupation_ai_demographic_distributions`.
- Atlas AI-exposure gallery with side-by-side measures and divergence view.
- Uncertainty metadata for exposure-measure disagreement.

## Acceptance Gates

- At least Eloundou plus Felten can be queried side by side.
- No headline output relies on a single exposure score.
- Crosswalk transformations are versioned and reversible where possible.
- Atlas shows exposure quartiles by demographic and geography using fixtures or ingested data.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
