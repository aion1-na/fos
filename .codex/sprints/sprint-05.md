# Sprint 05: Backtest Anchor Validation Substrate

Objective: build the validation substrate for retrodicting known trade and technology shocks before forward AI scenarios are trusted.

## Deliverables

- Bulk replication connector pattern hardened for Stata `.dta` and `.do` archives.
- `features.adh_china_shock_panel` and `features.pntr_mortality_backtest`.
- Robot exposure feature tables.
- Atlas backtest viewer with geography and demographic slices.
- Validation gate spec for China-shock backtest.

## Acceptance Gates

- Replication archives land immutably with checksums and source citations.
- Parsing preserves Stata labels and source variable names.
- Backtest feature tables carry provenance to raw archive hashes.
- Validation harness fails closed if backtest references are missing.

## Constraints

- Do not fabricate data. Use fixtures or request-status stubs where access is not approved.
- Every production dataset needs dataset card, license metadata, codebook mapping, quality profile, provenance manifest, and access policy.
- Every simulation-facing output must use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
- Keep diffs scoped to this sprint.
- Live network access is allowed only through explicit smoke-test commands and approved public endpoints or approved credentials.
