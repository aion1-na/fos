from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="FOS Data Service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "data-service"}


@app.get("/datasets")
def list_datasets() -> dict[str, list[dict[str, str]]]:
    return {
        "datasets": [
            {
                "canonical_dataset_name": "hrs",
                "access_status": "request_status_stub",
                "version": "access-not-approved",
            },
            {
                "canonical_dataset_name": "gfs",
                "access_status": "request_status_stub",
                "version": "access-not-approved",
            },
        ]
    }
