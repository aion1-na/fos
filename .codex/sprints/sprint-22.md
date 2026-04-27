# Sprint 22: Restricted Health and Mortality Path

## Objective

Set up the restricted-use health/mortality path needed for high-confidence deaths-of-despair and health-domain validation.

## Deliverables

- NCHS access tracker.
- IRB/DUA document checklist.
- Restricted mortality aggregate-result schema.
- State vital statistics opportunity map.
- Health-to-mortality calibration analysis plan.

## Acceptance Gates

- Small-cell suppression and disclosure constraints are codified.
- Restricted health outputs are clearly separated from public CDC WONDER outputs.
- Every aggregate result includes approval status and source environment metadata.
- No prohibited geography or demographic detail is exposed in Atlas.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
