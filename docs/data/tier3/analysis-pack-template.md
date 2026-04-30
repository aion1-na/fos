# Tier 3 Analysis-Pack Template

Use this template for every external secure-environment repository.

## Required Manifest Fields

- `project_id`
- `environment`
- `restricted_dataset_name`
- `access_status`
- `raw_restricted_data_in_fos_allowed`
- `code_ref`
- `code_hash`
- `environment_ref`
- `environment_hash`
- `intended_outputs`
- `owner`
- `timeline`

## Repository Contents

- `README.md`: project purpose, owner, and secure-environment location.
- `manifest.json`: the secure analysis manifest.
- `environment.lock`: exact software environment or container digest.
- `src/`: analysis code only; no restricted raw data.
- `outputs/README.md`: intended aggregate output names and disclosure-review routing.

## Rules

- Pin code and environment hashes before any secure run.
- Declare intended outputs before running the analysis.
- Do not commit credentials, extracts, row-level restricted data, or screenshots containing restricted data.
- Only aggregate outputs with approved disclosure-review metadata may enter FOS.
