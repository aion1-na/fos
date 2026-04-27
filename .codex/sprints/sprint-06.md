# Sprint 06: Evidence Graph and Intervention Priors

Objective: turn policy/intervention priors into auditable evidence claims linked to source datasets and literature.

## Deliverables

- `EvidenceClaim` schema and `evidence_graph` namespace.
- Postgres + AGE initialization and claim/citation/causal-edge migrations.
- Connectors or request-stub records for each intervention source.
- `features.intervention_effect_size_priors`.
- Atlas forest plot viewer with risk-of-bias and confidence labels.
- Curator review workflow.

## Acceptance Gates

- Every effect size has source, estimate, uncertainty, population, treatment, outcome, confidence label, and provenance link.
- By-request sources are represented as request status records, not fabricated microdata.
- Advisor-reviewed claims are distinguishable from draft claims.
- Atlas can trace claim -> source -> dataset card -> provenance manifest.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
