# Social Capital Context

Canonical dataset name: `social-capital-context`

Access status: fixture plus request-status stub

License metadata: source-specific public table and archive terms must be recorded before production ingestion.

Codebook mapping: `codebooks/social_capital_context_features.yaml`; maps trust, volunteering, civic engagement, and related social-capital measures into `features.social_capital_context`.

Quality profile: fixture rows test reversible construct mapping and valid geography joins. Production profiles must document coverage, time period, sampling error, and comparability limits.

Provenance manifest: `packages/data-pipelines/fixtures/community_context/community_pathways_fixture.csv` and `social_capital_archive_stub.json`.

Access policy: public aggregate rows can be used where terms permit. Archive-limited extracts remain request-status metadata until approved.

Public table versus microdata limitations: public aggregates support geography context only. Archive-limited microdata is not represented as fake tables.

Inappropriate uses: do not rank individuals or small groups by trust, civic engagement, volunteering, or social capital from aggregate indicators. Community participation variables are voluntary social pathways, not prescriptive recommendations.
