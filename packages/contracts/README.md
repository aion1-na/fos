# Contracts

Owner: Platform Contracts

Test command: `uv run pytest packages/contracts -v && pnpm --filter @fos/contracts test`

Definition of done:

- Pydantic and TypeScript contract exports are regenerated.
- JSON Schema exports are current.
- Contract changes preserve the kernel/pack seam.
- Data-facing outputs that cross into simulation use `dataset_reference = (canonical_dataset_name, version, content_hash)`.
