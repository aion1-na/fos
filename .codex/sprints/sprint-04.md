# Sprint 04: GFS Wave 1 Flourishing Measurement

Objective: make flourishing measurement operational through GFS Wave 1, methodology/codebooks, and cross-validation sources.

## Deliverables

- GFS connector with OSF/portal acquisition pattern and registration-gated license metadata.
- Scoring kernel with six-domain flourishing measures and sampling weight support.
- Cross-validation connectors for World Happiness Report, ESS, and WVS.
- `features.gfs_wave1_marginals_country_*`.
- Atlas per-domain distributions, heatmaps, demographic cuts, and country comparison panels.

## Acceptance Gates

- GFS cards display sampling design, weights, limitations, and citation instructions.
- Scoring kernel tests compare against known reference outputs where available.
- Atlas labels GFS Wave 1 as cross-sectional and research-grade, not prospective forecasting.
- Advisor review issue queue for GFS codebook mappings is populated.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
