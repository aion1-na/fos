# Contracts v0.1

Contracts are the typed seam between the kernel and packs. The kernel depends on `fw_contracts` and must not import from `packs/`.

## Version

`CONTRACTS_VERSION` is `0.1.0`. Packs assert this at load time through `assert_contracts_version`.

## Schema Exports

JSON Schema files are generated under `packages/contracts/schemas/v0.1/`. TypeScript contract parsers are generated under `packages/contracts/dist/ts/`.

## API Client

The FastAPI OpenAPI schema is generated into `packages/contracts/dist/api/openapi.json`. The published client export is:

```ts
import { getHealth } from "@fw/contracts/api";
```

Regenerate with:

```sh
uv run python tools/codegen/openapi_to_ts.py
```

CI fails if generated API files are stale.
