# Sprint 14: US Employment-Wellbeing Panel Stubs

Objective: Ingest the primary US panel datasets that move employment-to-flourishing transitions beyond literature priors.

Deliverables:
- Registration-gated connectors for HRS, MIDUS, NLSY79, NLSY97, and PSID.
- Harmonized panel codebooks and wave metadata.
- `features.us_employment_wellbeing_panels`.
- Attrition, missingness, and sampling-weight profiles.
- Atlas longitudinal panel availability cards.

Acceptance gates:
- Each panel has source-specific and canonical variable mappings.
- Employment status, income, health, depression/well-being, household, and demographic constructs harmonize consistently.
- DUA restrictions are enforced by access policy.
- Feature tables are usable by transition-model training code.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Live network access is allowed only through explicit network smoke-test command and only for approved public endpoints or approved credentials.
