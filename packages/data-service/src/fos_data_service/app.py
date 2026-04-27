from __future__ import annotations

from fastapi import FastAPI
from pydantic import ValidationError

from fw_contracts import DatasetReference
from fos_data_service.catalog import (
    Catalog,
    DataServiceError,
    DatasetRecord,
    DatasetReferenceSchemaError,
)

app = FastAPI(title="FOS Data Service")
catalog = Catalog()

FIXTURE_REFERENCE = DatasetReference(
    canonical_dataset_name="features.community_context",
    version="fixture-0.1",
    content_hash="a" * 64,
)
OLD_FIXTURE_REFERENCE = DatasetReference(
    canonical_dataset_name="features.community_context",
    version="fixture-0.0",
    content_hash="b" * 64,
)
for reference in [OLD_FIXTURE_REFERENCE, FIXTURE_REFERENCE]:
    catalog.register_dataset_record(
        DatasetRecord(
            reference=reference,
            card_path="docs/data/datasets/community-pathways.md",
            manifest_path=f"manifests/{reference.version}/community-context.json",
            upstream_references=(),
            consumed_by_runs=("simulation-run-fdw-smoke",),
            claim_ids=("claim_mentoring_meaning_v0",),
        )
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "data-service"}


def structured_error(error: DataServiceError) -> dict[str, str]:
    return {"error": error.code, "message": error.message}


def _reference_from_parts(
    canonical_dataset_name: str,
    version: str | None,
    content_hash: str | None,
) -> DatasetReference:
    if version is None or content_hash is None:
        raise DatasetReferenceSchemaError(
            "dataset_reference requires canonical_dataset_name, version, and content_hash"
        )
    try:
        return DatasetReference(
            canonical_dataset_name=canonical_dataset_name,
            version=version,
            content_hash=content_hash,
        )
    except ValidationError as exc:
        raise DatasetReferenceSchemaError(str(exc)) from exc


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


@app.get("/datasets/{canonical_dataset_name}/resolve")
def resolve_dataset(
    canonical_dataset_name: str,
    version: str | None = None,
    content_hash: str | None = None,
) -> dict[str, object]:
    try:
        reference = _reference_from_parts(canonical_dataset_name, version, content_hash)
        record = catalog.resolve_dataset_reference(reference)
    except DataServiceError as exc:
        return structured_error(exc)
    return {
        "dataset_reference": record.reference.model_dump(mode="json"),
        "card_path": record.card_path,
        "manifest_path": record.manifest_path,
    }


@app.get("/datasets/{canonical_dataset_name}/card")
def dataset_card(
    canonical_dataset_name: str,
    version: str | None = None,
    content_hash: str | None = None,
) -> dict[str, object]:
    resolved = resolve_dataset(canonical_dataset_name, version, content_hash)
    if "error" in resolved:
        return resolved
    return {
        "dataset_reference": resolved["dataset_reference"],
        "card_path": resolved["card_path"],
    }


@app.get("/datasets/{canonical_dataset_name}/manifest")
def dataset_manifest(
    canonical_dataset_name: str,
    version: str | None = None,
    content_hash: str | None = None,
) -> dict[str, object]:
    resolved = resolve_dataset(canonical_dataset_name, version, content_hash)
    if "error" in resolved:
        return resolved
    return {
        "dataset_reference": resolved["dataset_reference"],
        "manifest_path": resolved["manifest_path"],
    }


@app.get("/datasets/{canonical_dataset_name}/lineage")
def dataset_lineage(
    canonical_dataset_name: str,
    version: str | None = None,
    content_hash: str | None = None,
) -> dict[str, object]:
    try:
        reference = _reference_from_parts(canonical_dataset_name, version, content_hash)
        record = catalog.resolve_dataset_reference(reference)
    except DataServiceError as exc:
        return structured_error(exc)
    return {
        "dataset_reference": record.reference.model_dump(mode="json"),
        "upstream": [item.model_dump(mode="json") for item in record.upstream_references],
        "downstream": list(record.consumed_by_runs),
    }


@app.get("/claims/{claim_id}")
def claim_lookup(claim_id: str) -> dict[str, object]:
    matches = [
        record.reference.model_dump(mode="json")
        for record in catalog.dataset_records.values()
        if claim_id in record.claim_ids
    ]
    if not matches:
        return {"error": "missing_claim", "message": f"claim {claim_id} is not registered"}
    return {"claim_id": claim_id, "dataset_references": matches}


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
