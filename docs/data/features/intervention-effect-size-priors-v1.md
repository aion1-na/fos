# Feature Table: Intervention Effect Size Priors V1

Canonical dataset name: `features.intervention_effect_size_priors_v1`

Version: `request-status-v0.1`

Access status: fixture_only unit-test priors plus request-status literature sources

License metadata: source-specific literature extraction rights are pending; restricted extracts and by-request datasets remain request-status records.

Codebook mapping: `codebooks/intervention_effect_size_priors_v1.yaml`

Quality profile: fixture_only rows validate schema, review routing, transportability labels, and query surfaces. Production use requires advisor-approved extraction, risk-of-bias review, and source-specific provenance.

Provenance manifest: content hash is computed from `packages/data-pipelines/fixtures/evidence_graph/evidence_claims_fixture_only.json` and `packages/data-pipelines/fixtures/evidence_graph/intervention_sources_fixture_only.json`.

Access policy: do not commit restricted microdata or licensed full-text extracts. By-request sources must remain request-status metadata until approved.

Limitations: fixture_only priors are not empirical production estimates. Concordia may receive these rows as qualitative scene context only and cannot create causal effect sizes.

Inappropriate uses: do not treat draft, rejected, superseded, null-placeholder, or fixture_only claims as validated intervention effects.
