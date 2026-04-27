# Health-to-Mortality Calibration Analysis Plan

## Purpose

Prepare a restricted-use validation path for high-confidence deaths-of-despair and health-domain mortality calibration.

## Inputs

- NCHS restricted mortality aggregates, pending RDC access.
- State vital statistics aggregate outputs, pending state-specific DUAs.
- Public CDC WONDER remains a separate public-table reference path.

## Disclosure Constraints

- Minimum unsuppressed cell count: 10.
- Suppressed rows must not expose deaths or mortality rates.
- Atlas-visible geography is limited to national, state, or region.
- Atlas-visible demographic fields are limited to broad age band, sex, and cause group.

## Intended Aggregate Outputs

- `restricted_deaths_of_despair_rate_by_state_age_band`
- `restricted_health_to_mortality_calibration_by_cause_group`

## FDW Boundary

Raw restricted data does not enter FDW. Only disclosure-approved aggregate results with source environment metadata may be registered.
