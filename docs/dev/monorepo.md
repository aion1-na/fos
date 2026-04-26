# FOS Monorepo

FOS is a pnpm + uv monorepo. Python packages live under `packages/` and `packs/`; applications live under `apps/`.

## Layout

- `packages/contracts`: Pydantic and generated TypeScript contract seam.
- `packages/sim-kernel`: deterministic vectorized runtime.
- `packages/population-synth`: pack-agnostic population synthesis and snapshot storage.
- `packages/validation-core`: validation helpers for run reports.
- `packages/render-core`: shared render data helpers.
- `packs/toy-sir`: canary pack that exercises the contract without flourishing concepts.
- `packs/flourishing`: first content-bearing pack.
- `apps/api`: FastAPI service.
- `apps/studio`: Next.js Studio shell and stage surfaces.

## Common Commands

- `uv sync --all-packages`
- `pnpm install --frozen-lockfile`
- `make ci`
- `make up`
- `curl -fsSL http://localhost:8000/health`

## Release Gate

`make ci` is the local gate. GitHub CI adds import seam linting, pack linting, OpenAPI client drift checks, performance budget checks, Python tests, and Node tests.
