# Dataset Card: CDC Public Health Tables

Canonical dataset name: `cdc_public_health`

Version: `fixture-0.1`

Access status: fixture; public tables only unless source terms approve more

License metadata: pending source-specific review

Codebook mapping: `codebooks/cdc_public_health.yaml`; fixture preserves source names

Quality profile: mortality rows below the public-use cell threshold are suppressed

Provenance manifest: fixture hash generated in tests

Access policy: public tables may be used when published; microdata requires separate approval

Limitations: public table aggregates differ from governed microdata and may suppress small cells.

Inappropriate uses: do not expose mortality cells below suppression thresholds or treat public tables as restricted microdata outputs.
