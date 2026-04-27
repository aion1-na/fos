# Tier 1 v1.0.0 Release Notes

This MVP release pins the Tier 1 corpus to content-addressed fixture and request-status artifacts. It does not promote restricted or license-constrained data to production use.

Included datasets:
- ACS/IPUMS fixture
- O*NET fixture
- BLS OEWS fixture
- GFS Wave 1 fixture/request-status metadata
- Community pathways fixture

Reproducibility bundle:
- Release manifest: `docs/data/releases/tier1-v1.0.0.json`
- Provenance manifest: `docs/data/releases/tier1-v1.0.0-provenance.json`
- Smoke run id: `mvp-tier1-smoke`

All simulation-facing reads must use the pinned dataset reference tuple from the manifest.
