# Dataset Card: CDC Public Health Tables

Canonical dataset name: `cdc_public_health`

Version: `fixture-0.1`

Access status: fixture; public tables only unless source terms approve more

License metadata: pending source-specific review

Codebook mapping: `codebooks/cdc_public_health.yaml`; fixture preserves source names

Quality profile: mortality rows below the public-use cell threshold are suppressed; fixture content hash `2954e26e4645106cb79fc671bdc53faec90f4e4d1e30a5f248ea2d74dddc0edb`

Provenance manifest: `docs/data/releases/tier1-v1.0.0-provenance.json`; source artifact `packages/data-pipelines/fixtures/health_public/cdc_mortality_fixture_only.csv`

Access policy: public tables may be used when published; microdata requires separate approval

Limitations: public table aggregates differ from governed microdata and may suppress small cells.

Pathway role: health tables are validation context, not causal proof by themselves.

Inappropriate uses: do not expose mortality cells below suppression thresholds or treat public tables as restricted microdata outputs.
