# Sprint 21: Tier 3 Secure Analysis Preparation

## Objective

Prepare for Tier 3 secure-environment analyses without contaminating the central warehouse with restricted data.

## Deliverables

- RDC project tracker and analysis-pack repository template.
- Secure analysis manifest schema for external/RDC runs.
- Aggregate-result ingestion connector.
- Disclosure-review checklist.
- LEHD analysis plan for displacement calibration.

## Acceptance Gates

- Tier 3 raw restricted data is never stored in FOS unless allowed by terms.
- Only approved aggregate outputs enter the FOS with disclosure-review metadata.
- RDC analysis packs pin code, environment, and intended outputs.
- Census RDC timeline and owners are visible to leadership.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
