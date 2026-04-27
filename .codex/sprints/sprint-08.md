# Sprint 08: Community Pathways and Evidence Navigation

Objective: Parameterize network and institutional pathways while making evidence graph navigation visible in Atlas.

Deliverables:
- Connectors and dataset cards for social/community datasets.
- `features.community_context`, `features.time_use_context`, and `features.social_capital_context`.
- Religious attendance, civic engagement, trust, volunteering, mobility, and household context mappings.
- Atlas evidence graph explorer using React Flow node and edge semantics.
- Search filters by construct, claim, source, and confidence label.

Acceptance gates:
- Community-pathway features join to county, ZIP, or tract only where legally and methodologically valid.
- Unsupported or archive-limited data receives request-stub status, not fabricated tables.
- Graph explorer can traverse construct -> evidence claim -> citation -> dataset.
- Dataset cards disclose limitations and inappropriate uses.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
