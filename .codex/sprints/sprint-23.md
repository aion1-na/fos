# Sprint 23: Administrative Displacement and Healthcare Utilization Truth Data

## Objective

Build the operational path for administrative displacement and healthcare utilization truth data.

## Deliverables

- State partnership target matrix.
- Administrative-data DUA tracker.
- Claims-data connector contract and aggregate-result schemas.
- Healthcare utilization outcome taxonomy.
- State UI job-loss/reemployment/wage-trajectory analysis plan.

## Acceptance Gates

- State and claims workflows require license/IRB/legal sign-off before ingestion.
- Outcome taxonomy maps claims/utilization to physical-health domain cautiously.
- Administrative-data findings can return as approved aggregate calibration tables.
- No paid license is assumed available without explicit status.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
