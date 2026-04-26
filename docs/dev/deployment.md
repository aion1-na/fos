# Deployment

Local services run through Docker Compose:

```sh
make up
make down
```

The stack contains Postgres 15, MinIO, MLflow, the FastAPI API, and Studio.

## API

FastAPI serves:

- `GET /health`
- `GET /openapi.json`
- population, scenario, run, validation, finding, override, and brief endpoints.

## Brief Signing

Signed bundle export uses `FOS_BRIEF_SIGNING_KEY` in CI. Local development falls back to a deterministic development key.
