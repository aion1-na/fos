# Sprint 18: Real-Time Labor Partner Feeds

Objective: Close the gap between annual public sources and current AI deployment/hiring dynamics.

Deliverables:
- Partner-feed connector pattern with daily/hourly partition snapshots.
- Commercial data evaluation checklist and license constraints.
- Lightcast, LinkedIn, and Indeed POC connectors or synthetic contract tests.
- `features.real_time_labor_signals`.
- Run-submission snapshot policy.

Acceptance gates:
- Commercial and partnership feeds are compartmentalized by license.
- Every snapshot is content-addressed and can be pinned by a run manifest.
- POC connectors can be tested without exposing secrets.
- Atlas labels real-time feeds as deployment signals distinct from predicted exposure.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Live network access is allowed only through explicit network smoke-test command and only for approved public endpoints or approved credentials.
