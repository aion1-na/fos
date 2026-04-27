# Sprint 00: Data Arc Project Setup

Objective: make the data workstream a first-class Codex project with explicit ownership, safe defaults, source-control discipline, shared contracts, partnership trackers, and clear boundaries between platform and data responsibilities.

## Deliverables

- Monorepo structure with `packages/data-pipelines`, `packages/data-service`, `packages/contracts`, `apps/atlas`, `infra`, `docs`, and `.codex`.
- `.codex/instructions.md` forbids fake data, unversioned reads, undocumented transformations, and silent schema changes.
- DUA and partnership trackers for HRS, SOEP, Understanding Society, GFS, Anthropic Economic Index, Census RDC, and commercial labor data.
- Initial requirements traceability matrix and operating cadence.

## Acceptance Gates

- Repository builds from a clean checkout.
- All data workstream packages have README, owner, test command, and definition of done.
- Human-readable backlog maps every DRD section to a sprint.
- No connector or dashboard code uses real credentials in source control.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Do not use network access in this sprint.
