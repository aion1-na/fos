# Sprint 12: MVP Tier 1 Data Release

Objective: Ship the MVP against version-locked Tier 1 data with full provenance and a clear path into Tier 2 onboarding.

Deliverables:
- v1.0.0 Tier 1 release manifest.
- Immutable artifact retention policy.
- Release notes and reproducibility bundle.
- Runbook for re-fetching periodic sources without breaking pinned runs.
- DUA submission checklist and status updates.
- MVP data-service deployment checklist.

Acceptance gates:
- Fresh environment can resolve every v1.0.0 `dataset_reference`.
- Release manifest includes hashes, connector versions, codebook versions, license classes, and card URLs.
- MVP smoke run succeeds with full provenance manifest.
- Tier 2 DUA tracker has named owners and dates.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
