# Sprint 02: Codebooks, Public Input Fixtures, and Atlas Shell

Objective: stand up the canonical construct dictionary, key demographic/occupation/wage inputs, and the first stakeholder-visible Atlas shell.

## Deliverables

- `codebooks/constructs.yaml` v0.1.
- `codebooks/acs_*.yaml`, `onet.yaml`, and `bls_oews.yaml`.
- Offline-safe connectors for ACS/IPUMS, O*NET API, and BLS OEWS API.
- Atlas Next.js skeleton with dataset directory.
- Dataset card renderer and Markdown card template.

## Acceptance Gates

- ACS, O*NET, and BLS fixtures parse to staged Parquet.
- Codebook mappings preserve original labels and canonical names.
- Atlas can list datasets, versions, licenses, content hashes, fetch timestamps, and card links.
- Scientific review queue exists for construct changes.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
