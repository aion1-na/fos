# Sprint 09: Tier 1 Quality Gates

Objective: Move from many connectors to a trustworthy Tier 1 corpus with repeatable validation and complete documentation.

Deliverables:
- Expectation suites for every Tier 1 dataset.
- Pandera-style schemas for staged, harmonized, and feature tables.
- Dataset-card completeness linter.
- License/access policy checks in catalog API.
- Atlas completeness dashboard.
- Release candidate manifest for Tier 1.

Acceptance gates:
- No Tier 1 dataset can be marked production-ready without card, license, codebook, quality profile, provenance, and access policy metadata.
- Quality gates report row counts, missingness, distributions, PII candidates, and sampling metadata.
- Atlas clearly labels data tier and dataset status.
- CI fails when a production dataset is missing required metadata.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
