# Run-Submission Snapshot Policy

Every run that consumes real-time labor signals must pin a content-addressed snapshot reference before execution.

Required tuple:

`dataset_reference = (canonical_dataset_name, version, content_hash)`

Rules:
- Use daily partitions for batch partner feeds and hourly partitions only when the license allows it.
- Never read "latest" during a run.
- Never overwrite a snapshot at an existing content hash.
- Store vendor-specific snapshots in license compartments.
- Record the pinned snapshot in the run manifest and reproducibility bundle.
