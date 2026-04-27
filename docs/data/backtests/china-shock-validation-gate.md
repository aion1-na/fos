# Validation Gate: China Shock Backtest

Owner: Validation Lead

Gate id: `china_shock_backtest_v0.1`

Fail-closed rule: validation fails if any required backtest reference is missing.

Required references:

- `features.adh_china_shock_panel`
- raw ADH archive content hash
- connector version
- source citation
- Stata variable label manifest

Pass criteria:

- feature rows retain provenance to raw archive hash
- Stata source variable names and labels are preserved
- geography slices are available
- demographic slices are available where fixture/source permits
