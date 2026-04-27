# Data Infrastructure

Owner: Platform Engineering

Test command: `pnpm -r lint && uv run pytest tests -v`

Definition of done:

- Infrastructure examples use placeholders only.
- Secrets are referenced by environment variable name, never committed value.
- Production dataset storage paths are versioned and policy-bound.
- Access logs and provenance manifests are required for approved datasets.
