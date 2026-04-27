# Sprint 07: Public Health Validation and International Policy Context

Objective: complete the public health-domain validation substrate and cross-country policy-regime context.

## Deliverables

- Connectors for CDC, BRFSS, NHIS, NHANES, and MEPS where public.
- Small-cell suppression and mortality data policy checks.
- OECD, World Bank, Eurostat, and ILO connector family.
- `features.health_validation_context` and `features.policy_regime_context`.
- Cross-country materialized dashboard views.

## Acceptance Gates

- Mortality outputs respect public-use cell suppression rules.
- Country identifiers map to ISO3 and preserve source country codes.
- OECD safety-net indicators are queryable alongside flourishing and employment indicators.
- International data cards document public table versus microdata limitations.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
