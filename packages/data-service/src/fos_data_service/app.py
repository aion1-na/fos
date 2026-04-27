from __future__ import annotations

from fastapi import FastAPI
from pydantic import ValidationError

from fw_contracts import DatasetReference
from fos_data_service.catalog import (
    AtlasAccessPolicy,
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
TIER1_V1_REFERENCES = [
    DatasetReference(
        canonical_dataset_name="acs-ipums",
        version="1.0.0",
        content_hash="4b064f72dee92ed13a4dbb7945d29e04184199c6e8da67013a6a0c0cb3de9eb9",
    ),
    DatasetReference(
        canonical_dataset_name="onet",
        version="1.0.0",
        content_hash="9e62214c0f58829191797b942a49e691f1065996a1e445ce4c62f8ea9e84a405",
    ),
    DatasetReference(
        canonical_dataset_name="bls-oews",
        version="1.0.0",
        content_hash="0d5bd5e75a3367a632677ef51aa22949353c4d1db723716165e5137692e21d95",
    ),
    DatasetReference(
        canonical_dataset_name="gfs-wave1",
        version="1.0.0",
        content_hash="8630b7664865a8ea63fa4ebb7bed3224aeb97f7db3cddefd112003ce6bef2545",
    ),
    DatasetReference(
        canonical_dataset_name="community-pathways",
        version="1.0.0",
        content_hash="fb28f7b26a0e4047627607aecb9249c45d2a678b34bdda3a34d886810613483a",
    ),
]
CARD_PATHS = {
    "acs-ipums": "docs/data/datasets/acs-ipums.md",
    "onet": "docs/data/datasets/onet.md",
    "bls-oews": "docs/data/datasets/bls-oews.md",
    "gfs-wave1": "docs/data/datasets/gfs-wave1.md",
    "community-pathways": "docs/data/datasets/community-pathways.md",
    "features.community_context": "docs/data/datasets/community-pathways.md",
}

for reference in [OLD_FIXTURE_REFERENCE, FIXTURE_REFERENCE, *TIER1_V1_REFERENCES]:
    catalog.register_dataset_record(
        DatasetRecord(
            reference=reference,
            card_path=CARD_PATHS[reference.canonical_dataset_name],
            manifest_path=(
                "docs/data/releases/tier1-v1.0.0-provenance.json"
                if reference.version == "1.0.0"
                else f"manifests/{reference.version}/community-context.json"
            ),
            upstream_references=(),
            consumed_by_runs=(
                ("mvp-tier1-smoke",)
                if reference.version == "1.0.0"
                else ("simulation-run-fdw-smoke",)
            ),
            claim_ids=("claim_mentoring_meaning_v0",),
        )
    )

for policy in [
    AtlasAccessPolicy(
        canonical_dataset_name="community-pathways",
        scope="public",
        tier="Tier 1",
        status="fixture",
        limitations="Fixture-only public aggregate context; no individual inference.",
        provenance_link="docs/data/datasets/community-pathways.md",
    ),
    AtlasAccessPolicy(
        canonical_dataset_name="hrs",
        scope="private",
        tier="Tier 1",
        status="request_status_stub",
        limitations="DUA-gated; no public data rows in repository.",
        provenance_link="docs/data/datasets/hrs.md",
        gated_reason="restricted_data_access",
    ),
    AtlasAccessPolicy(
        canonical_dataset_name="commercial-labor-data",
        scope="private",
        tier="Tier 1",
        status="request_status_stub",
        limitations="License-constrained vendor data; request-status only.",
        provenance_link="docs/data/datasets/commercial-labor-data.md",
        gated_reason="license_constrained",
    ),
]:
    catalog.register_atlas_access_policy(policy)


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


def _policy_payload(policy: AtlasAccessPolicy) -> dict[str, object]:
    return {
        "canonical_dataset_name": policy.canonical_dataset_name,
        "scope": policy.scope,
        "tier": policy.tier,
        "status": policy.status,
        "limitations": policy.limitations,
        "provenance_link": policy.provenance_link,
        "gated_reason": policy.gated_reason,
    }


@app.get("/atlas/public")
def public_atlas_subset() -> dict[str, list[dict[str, object]]]:
    return {"datasets": [_policy_payload(policy) for policy in catalog.public_atlas_policies()]}


@app.get("/atlas/private")
def private_atlas_inventory() -> dict[str, list[dict[str, object]]]:
    return {"datasets": [_policy_payload(policy) for policy in catalog.private_atlas_policies()]}


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
