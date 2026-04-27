# Data Pipelines

Owner: Data Engineering

Test command: `uv run pytest packages/data-pipelines -v`

Definition of done:

- Reads only versioned fixture or approved production dataset references.
- Emits `dataset_reference = (canonical_dataset_name, version, content_hash)` for every simulation-facing output.
- Writes a provenance manifest for each output.
- Documents transformations and codebook mappings before merge.

This package contains offline-safe pipeline primitives and request-status stubs. It must not contain production credentials or fabricated source data.
