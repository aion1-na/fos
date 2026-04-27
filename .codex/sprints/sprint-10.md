# Sprint 10: Dataset Reference Platform Contract

Objective: Connect the data workstream to the MVP platform through a small typed content-addressed contract.

Deliverables:
- Shared Pydantic and TypeScript `dataset_reference` schema.
- FastAPI endpoints for resolve, card, manifest, lineage, and claim lookup.
- Structured errors for missing datasets and schema breaks.
- Atlas lineage graph: upstream/downstream and simulation runs.
- Platform smoke-test fixture showing an end-to-end run consuming FDW data.

Acceptance gates:
- No unversioned reads are possible through the data-service.
- Simulation smoke test records every `dataset_reference` it touched.
- Old versions remain resolvable after a new version is registered.
- Atlas provenance view can answer what fed this dataset and what consumed it.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
