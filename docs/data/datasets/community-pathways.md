# Community Pathways

Canonical dataset name: `community-pathways`

Access status: fixture plus request-status stubs

License metadata: public/community tables vary by source; archive-limited sources require source approval before production use.

Codebook mapping: `codebooks/community_context_features.yaml`; maps religious attendance, civic engagement, trust, volunteering, mobility, and household context into construct-specific pathway features while preserving source geography identifiers and labels.

Quality profile: fixture rows are used only for parser, join-validity, and provenance tests. Production quality profiles must document geography coverage, suppression rules, source year, missingness, and construct validity.

Provenance manifest: `packages/data-pipelines/fixtures/community_context/community_pathways_fixture.csv`, `time_use_fixture.csv`, `household_context_fixture.csv`, and request-status stub files.

Access policy: public tables may be staged when license terms allow it. Archive-limited or unapproved microdata must remain request-status metadata until access is approved.

Public table versus microdata limitations: public aggregate tables can support county, ZIP, tract, or national context where the geography is legally and methodologically valid. Individual-level religious attendance, diary, and restricted social-capital archives cannot be backfilled with synthetic rows.

Inappropriate uses: do not infer individual religious behavior, household composition, trust, volunteering, or mobility from aggregate geography-level context. Do not join to geography levels that the source does not support. Religious and community participation variables are voluntary social pathways, not prescriptive recommendations.
