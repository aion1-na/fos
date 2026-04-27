# Sprint 13: Tier 2 Longitudinal Panel Readiness

Objective: Prepare the warehouse for longitudinal panels while keeping DUA and license boundaries enforceable.

Deliverables:
- `Tier2AccessRequest` model and dashboard.
- Secure storage compartments and access-policy tests.
- Panel schema with `person_id`, `household_id`, `wave`, `country`, `weights`, `outcomes`, `treatments`, and attrition metadata.
- TimescaleDB migrations and materialized panel views.
- Connector stubs for all pending DUA sources.

Acceptance gates:
- No Tier 2 source can be ingested without approved license/access status.
- Unauthorized users receive structured denial, not hidden data leakage.
- Panel schema supports wave-level and person-level longitudinal queries.
- DUA status is visible in Atlas/admin but not public.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
