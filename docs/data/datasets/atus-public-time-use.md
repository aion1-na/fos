# ATUS Public Time Use

Canonical dataset name: `atus-public-time-use`

Access status: fixture plus public-table placeholder

License metadata: public-use table metadata must be checked before production ingestion.

Codebook mapping: `codebooks/time_use_context_features.yaml`; maps time-use measures such as caregiving and social time into `features.time_use_context`.

Quality profile: fixture rows validate schema, units, and dataset references only. Production profiles must document survey design, weights, table vintage, and missing categories.

Provenance manifest: `packages/data-pipelines/fixtures/community_context/time_use_fixture.csv`.

Access policy: public aggregate tables only unless governed microdata access is approved.

Public table versus microdata limitations: public tables are suitable for broad context, not individual diary reconstruction.

Inappropriate uses: do not use public aggregates to infer a specific person's schedule or behavioral sequence.
