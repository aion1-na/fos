# Dataset Reference Contract

Every simulation-facing data output must include:

```text
dataset_reference = (canonical_dataset_name, version, content_hash)
```

Definitions:

- `canonical_dataset_name`: lowercase stable identifier, for example `hrs` or `gfs`.
- `version`: source release, fixture version, or `access-not-approved` for request-status stubs.
- `content_hash`: SHA-256 hash of the exact bytes used to produce the output.

Unversioned reads are forbidden. Request-status stubs may describe access progress but must not masquerade as production data.
