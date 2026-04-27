# Data Workstream

Owner: Data Lead

Test command: `uv run pytest packages/data-pipelines packages/data-service tests/test_data_workstream.py -v`

Definition of done:

- Access status is explicit.
- No real data or credentials are committed.
- Dataset references are content-addressed.
- Production readiness metadata exists before production reads.

The data workstream owns dataset acquisition, DUA/partnership tracking, codebook mapping, quality profiling, provenance, and metadata service boundaries. Platform owns simulation runtime, Studio workflow surfaces, and pack execution.
