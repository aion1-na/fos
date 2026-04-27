# Requirements Traceability Matrix

| Requirement | Source | Owner | Sprint | Artifact | Status |
| --- | --- | --- | --- | --- | --- |
| First-class data packages | Sprint 00 objective | Data Engineering | 00 | `packages/data-pipelines`, `packages/data-service` | Implemented scaffold |
| Atlas metadata app boundary | Sprint 00 objective | Data Product | 00 | `apps/atlas` | Implemented scaffold |
| Safe Codex defaults | Sprint 00 constraints | Data Lead | 00 | `.codex/instructions.md` | Implemented |
| DUA and partnership trackers | Sprint 00 deliverables | Partnerships | 00 | `docs/data/partnerships/*.md` | Request-status stubs |
| Production dataset metadata minimum | Sprint 00 constraints | Data Governance | 00 | `docs/data/datasets/*.md` | Stub cards |
| Dataset reference tuple | Sprint 00 constraints | Contracts | 00 | `docs/data/dataset-reference-contract.md` | Implemented |
| DRD backlog mapping | Sprint 00 acceptance | Data Lead | 00 | `docs/data/backlog.md` | Implemented |
| Credential safety | Sprint 00 acceptance | Security | 00 | `tests/test_data_workstream.py` | Implemented |
| Connector contract | Sprint 01 deliverable | Data Engineering | 01 | `packages/data-pipelines/src/fos_data_pipelines/models.py` | Implemented |
| Raw landing determinism | Sprint 01 acceptance | Data Engineering | 01 | `packages/data-pipelines/src/fos_data_pipelines/raw_zone.py` | Implemented |
| Postgres catalog migration | Sprint 01 deliverable | Data Platform | 01 | `packages/data-service/migrations/001_catalog.sql` | Implemented |
| Artifact lineage lookup | Sprint 01 acceptance | Data Platform | 01 | `packages/data-service/src/fos_data_service/catalog.py` | Implemented |
| Platform raw-read boundary | Sprint 01 acceptance | Platform Engineering | 01 | `tests/test_data_workstream.py` | Implemented |
