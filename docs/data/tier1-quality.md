# Tier 1 Quality Gates

Sprint 09 defines Tier 1 as a release-candidate corpus, not a production corpus. Fixture-backed datasets and request-status stubs can pass metadata and schema validation, but they cannot be marked production-ready.

Required production metadata:
- Dataset card
- License metadata
- Codebook mapping
- Quality profile
- Provenance manifest
- Access policy

Quality reports include:
- Row counts
- Missingness by column
- Distribution summaries
- PII candidate columns
- Sampling metadata

No live network access is required or permitted for this sprint.
