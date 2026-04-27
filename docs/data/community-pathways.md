# Community Pathway Feature Notes

The Sprint 08 community pathway builders create three simulation-facing feature tables:

- `features.community_context`
- `features.time_use_context`
- `features.social_capital_context`

Every output row carries `dataset_reference = (canonical_dataset_name, version, content_hash)`.

Join discipline:
- County, ZIP, tract, and national joins are allowed only when the source fixture marks `join_allowed=true`.
- Individual or private-archive rows are filtered out of feature tables and represented as request-status stubs.
- Source geography identifiers and source labels are preserved for auditability.

Atlas navigation:
- The evidence graph explorer exposes construct -> evidence claim -> citation -> dataset traversal.
- Filters are represented for construct, claim, source, and confidence label.
