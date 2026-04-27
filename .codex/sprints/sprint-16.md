# Sprint 16: Cross-Country Employment-Wellbeing Panels

Objective: Operationalize the cross-country safety-net comparison that anchors the platform narrative.

Deliverables:
- International panel connector family.
- Cross-country canonical codebooks for employment, education, income, family, health, and well-being.
- `features.cross_country_employment_wellbeing_panels`.
- `features.safety_net_regime_comparators`.
- Atlas cross-country longitudinal comparison view.

Acceptance gates:
- Country, wave, weight, and sampling design metadata are preserved.
- Crosswalks document where constructs are comparable and where they are only approximate.
- Atlas can compare US, UK, Germany, Australia, and EU age-50+ panels when available.
- License boundaries remain enforceable per panel.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Live network access is allowed only through explicit network smoke-test command and only for approved public endpoints or approved credentials.
