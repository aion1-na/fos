# MVP Data-Service Deployment Checklist

- Confirm `docker compose config` succeeds.
- Confirm the service can resolve every `tier1-v1.0.0` dataset reference.
- Confirm `/atlas/public` excludes restricted and license-constrained data.
- Confirm release manifest and provenance manifest are mounted or packaged.
- Confirm no credentials are present in source control.
- Confirm artifact retention policy is linked in release notes.
- Confirm deployment environment uses read-only release artifacts for pinned runs.
