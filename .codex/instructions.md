# Data Workstream Operating Rules

These rules apply to all data workstream changes in this repository.

## Hard Prohibitions

- Do not fabricate data. Use fixtures or request-status stubs when access is not approved.
- Do not perform unversioned reads. Every dataset read must include canonical dataset name, version, and content hash.
- Do not make undocumented transformations. Every transformation must name its source fields, output fields, codebook mapping, and quality checks.
- Do not introduce silent schema changes. Schema changes require an updated contract, dataset card, codebook mapping, quality profile, provenance manifest, access policy, and review note.
- Do not commit real credentials, connector tokens, dashboard tokens, private URLs, DUA documents with restricted content, or raw production data.

## Production Dataset Minimum

Every production dataset must have:

- dataset card
- license metadata
- codebook mapping
- quality profile
- provenance manifest
- access policy

No production dataset is approved by default.

## Simulation-Facing Outputs

Every simulation-facing output must expose:

```text
dataset_reference = (canonical_dataset_name, version, content_hash)
```

Outputs missing this tuple are not allowed to cross into platform/runtime work.
