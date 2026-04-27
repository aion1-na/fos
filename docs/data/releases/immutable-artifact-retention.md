# Immutable Artifact Retention Policy

Tier 1 v1.0.0 artifacts are immutable once referenced by a release manifest.

Rules:
- Do not overwrite artifact bytes at an existing content hash.
- Do not delete artifacts referenced by a release manifest.
- Register refreshed source data as a new version and new content hash.
- Preserve old versions so pinned runs remain resolvable.
- Retain dataset cards, codebook versions, license classes, and provenance manifests with the release.

Exception handling:
- If an artifact must be withdrawn for legal reasons, replace it with a tombstone manifest preserving the dataset reference and withdrawal reason.
