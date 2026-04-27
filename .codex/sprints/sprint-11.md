# Sprint 11: Transparency and Scientific Governance

Objective: Prepare the transparency surface and scientific governance artifacts before MVP demos turn into claims.

Deliverables:
- Public/private view gating for Atlas.
- Search and citation generation across cards, codebooks, and evidence claims.
- Scientific review checklist and sign-off logs.
- OSF pre-registration draft packet.
- Brief template language for demo, research-grade, and decision-grade outputs.

Acceptance gates:
- Public Atlas subset excludes gated, restricted, and license-constrained data.
- Every public page displays data tier, limitations, and provenance links.
- Pre-registration packet includes scenario definition, validation gates, seed policy, and dataset version policy.
- Advisor sign-off status is visible per construct, codebook, and evidence claim.

Constraints:
- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint and do not commit automatically.
- Do not use network access in this sprint.
