from __future__ import annotations

from fastapi import FastAPI

from fos_data_service.catalog import Catalog

app = FastAPI(title="FOS Data Service")
catalog = Catalog()


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


@app.get("/datasets/{canonical_dataset_name}/policy")
def dataset_policy(canonical_dataset_name: str) -> dict[str, object]:
    policy = catalog.dataset_policy(canonical_dataset_name)
    if policy is None:
        return {
            "canonical_dataset_name": canonical_dataset_name,
            "policy": None,
            "can_mark_production_ready": False,
        }
    return {
        "canonical_dataset_name": policy.canonical_dataset_name,
        "tier": policy.tier,
        "status": policy.status,
        "production_ready": policy.production_ready,
        "missing_metadata": list(policy.missing_metadata),
        "can_mark_production_ready": policy.can_mark_production_ready,
    }


@app.get("/artifacts/{artifact_id}/lineage")
def artifact_lineage(artifact_id: str) -> dict[str, str] | dict[str, None]:
    lineage = catalog.artifact_lineage(artifact_id)
    if lineage is None:
        return {"artifact_id": artifact_id, "lineage": None}
    return {
        "artifact_id": lineage.artifact_id,
        "canonical_dataset_name": lineage.canonical_dataset_name,
        "dataset_version": lineage.dataset_version,
        "connector_name": lineage.connector_name,
        "connector_version": lineage.connector_version,
        "content_hash": lineage.content_hash,
    }
