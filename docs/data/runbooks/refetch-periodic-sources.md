# Runbook: Re-Fetching Periodic Sources

Purpose: refresh periodic public sources without breaking pinned runs.

Steps:
1. Create a new connector run with an explicit connector version.
2. Land raw bytes to a new content-addressed path.
3. Compute and record the new content hash.
4. Create a new dataset version; never mutate `1.0.0`.
5. Update the dataset card with fetch timestamp, license class, and limitations.
6. Run quality gates and metadata completeness checks.
7. Register the new dataset reference alongside old references.
8. Confirm all old release-manifest references still resolve.

No network fetch happens in Sprint 12; this runbook describes the controlled procedure for future approved refreshes.
