# Dataset Card: NHIS Public

Canonical dataset name: `nhis_public`

Version: `access-not-approved`

Access status: request-status stub

License metadata: pending source review

Codebook mapping: `codebooks/nhis_public.yaml`; request-status only until approved public table selection

Quality profile: request-status metadata only; production profiles must document public table vintage, weights, geography, missingness, and suppression; request-status artifact hash `4ca1ffe01b51559462b467429d921517025ceb74f0cbd608d12a19da194660b8`

Provenance manifest: `docs/data/releases/tier1-v1.0.0-provenance.json`; request-status source `packages/data-pipelines/fixtures/health_public/nhis_public_stub.json`

Access policy: public tables may be used when published; microdata requires separate approval

Limitations: public table versus microdata limitations must be documented before production use.

Inappropriate uses: do not infer individual health status, expose small cells, or treat public tables as governed microdata.
