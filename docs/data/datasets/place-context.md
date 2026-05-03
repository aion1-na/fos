# Dataset Card: Place Context

Canonical dataset name: `features.place_context`

Access status: fixture_only unit-test aggregates plus request-status records for unsupported or restricted sources

License metadata: source-specific public aggregate terms must be recorded before production ingestion. Restricted individual microdata is not represented as rows.

Codebook mapping: `codebooks/place_context_features.yaml`; maps Opportunity Atlas, OECD, World Bank, and related public place-context aggregates into documented geography and population join fields.

Quality profile: fixture_only rows validate legal geography joins, pathway role labels, dataset references, and request-status handling for unsupported individual-level records. Production profiles must document vintage, geography support, missingness, uncertainty, and comparability limits. Fixture content hash `018d3d86280b9bfded291887eeb83d289e0f7c3b6077f58d477dc9a24cbcece1`.

Provenance manifest: `docs/data/releases/tier1-v1.0.0-provenance.json`; source artifact `packages/data-pipelines/fixtures/community_context/place_context_fixture_only.csv`; restricted request-status artifact `packages/data-pipelines/fixtures/community_context/place_restricted_stub.json`.

Access policy: public aggregates may be used only at source-supported geography levels. Restricted tax, mobility, or individual archive records remain request-status metadata until access is approved.

Public aggregate versus microdata limitations: place features are contextual calibration or validation inputs. They do not prove causal effects and do not assign individual histories.

FOS population joins: supported joins are `county_fips`, `country_iso3`, `zip_code`, and `census_tract` where the source geography level is legally and methodologically valid.

Inappropriate uses: do not rank individuals, infer family histories, expose restricted details, or treat place context as causal proof without a validated design.
