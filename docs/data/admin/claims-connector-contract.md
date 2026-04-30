# Claims Connector Contract

Claims connectors are contract-tested without secrets until access is approved.

## Required Fields

- `connector_name`
- `connector_version`
- `vendor_or_steward`
- `workflow`
- `license_status`
- `paid_license_required`
- `secret_free_contract_test`
- `allowed_outputs`

## Rules

- Do not store real credentials in source control.
- Paid license feeds remain request-status stubs until explicit approval.
- Allowed outputs must be aggregate calibration families only.
- Row-level claims data does not enter FOS.
- Simulation-facing aggregate outputs use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
