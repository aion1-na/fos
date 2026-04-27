# LEHD Displacement Calibration Analysis Plan

## Purpose

Prepare a Census RDC analysis pack for LEHD-based displacement calibration. This is a request-status plan only; no LEHD data or restricted outputs are stored in the repository.

## Model Weakness

The displacement transition currently relies on literature priors and public aggregate backtests. The proposed secure analysis targets residual error around job-loss timing, reemployment timing, and wage trajectory after displacement.

## Intended Aggregate Outputs

- `lehd_displacement_event_rates_by_industry_region`
- `lehd_reemployment_latency_distribution`
- `lehd_wage_trajectory_bins_after_displacement`

## Secure Environment

- Environment: Census RDC.
- Data status: request_status_stub.
- Owner: Secure data lead.
- Timeline: 2026 Q3 proposal, 2026 Q4 disclosure-reviewed aggregates if approved.

## FDW Boundary

Raw LEHD restricted data must not enter FDW. Only approved aggregate outputs with disclosure-review metadata may be ingested.
