from __future__ import annotations

from fastapi import FastAPI
from pydantic import ValidationError

from fw_contracts import DatasetReference
from fos_data_service.catalog import (
    AtlasAccessPolicy,
    AccessDeniedError,
    Catalog,
    DataServiceError,
    DatasetRecord,
    DatasetReferenceSchemaError,
    Tier2AccessRequest,
    UserRole,
)
from fos_data_service.secure_analysis import (
    AggregateResultSubmission,
    SecureAnalysisManifest,
    ingest_restricted_aggregate,
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

for request in [
    Tier2AccessRequest(
        canonical_dataset_name="hrs",
        owner="Data partnerships lead",
        submitted_on=None,
        access_status="request_status_stub",
        license_status="not_approved",
        secure_compartment="tier2/hrs",
        requested_use="longitudinal retirement and health panel validation",
        updated_on="2026-05-15",
    ),
    Tier2AccessRequest(
        canonical_dataset_name="soep",
        owner="Data partnerships lead",
        submitted_on=None,
        access_status="request_status_stub",
        license_status="not_approved",
        secure_compartment="tier2/soep",
        requested_use="cross-country longitudinal panel validation",
        updated_on="2026-05-22",
    ),
    Tier2AccessRequest(
        canonical_dataset_name="understanding_society",
        owner="Data partnerships lead",
        submitted_on=None,
        access_status="request_status_stub",
        license_status="not_approved",
        secure_compartment="tier2/understanding_society",
        requested_use="UK longitudinal household panel validation",
        updated_on="2026-05-29",
    ),
    Tier2AccessRequest(
        canonical_dataset_name="census_rdc",
        owner="Secure data lead",
        submitted_on=None,
        access_status="request_status_stub",
        license_status="not_approved",
        secure_compartment="tier2/census_rdc",
        requested_use="restricted geographic validation after disclosure approval",
        updated_on="2026-06-05",
    ),
    Tier2AccessRequest(
        canonical_dataset_name="commercial_labor_data",
        owner="Partnerships lead",
        submitted_on=None,
        access_status="request_status_stub",
        license_status="not_approved",
        secure_compartment="tier2/commercial_labor_data",
        requested_use="licensed labor-market validation",
        updated_on="2026-06-12",
    ),
]:
    catalog.register_tier2_access_request(request)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "data-service"}


def structured_error(error: DataServiceError) -> dict[str, str]:
    return {"error": error.code, "message": error.message}


def _tier2_payload(request: Tier2AccessRequest) -> dict[str, object]:
    return {
        "canonical_dataset_name": request.canonical_dataset_name,
        "owner": request.owner,
        "submitted_on": request.submitted_on,
        "access_status": request.access_status,
        "license_status": request.license_status,
        "secure_compartment": request.secure_compartment,
        "requested_use": request.requested_use,
        "updated_on": request.updated_on,
        "ingest_allowed": request.ingest_allowed,
    }


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


RDC_TRACKER = [
    {
        "project_id": "census-rdc-lehd-displacement-calibration",
        "owner": "Secure data lead",
        "leadership_visible": True,
        "status": "request_status_stub",
        "next_action": "Submit Census RDC proposal package after scientific curator review.",
        "timeline": "2026 Q3 proposal, 2026 Q4 disclosure-reviewed aggregates if approved",
    }
]


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


@app.get("/secure-analysis/rdc-projects")
def rdc_project_tracker() -> dict[str, list[dict[str, object]]]:
    return {"projects": RDC_TRACKER}


@app.post("/secure-analysis/manifest/validate")
def validate_secure_analysis_manifest(manifest: SecureAnalysisManifest) -> dict[str, object]:
    return {
        "project_id": manifest.project_id,
        "environment": manifest.environment,
        "raw_restricted_data_in_fdw_allowed": manifest.raw_restricted_data_in_fdw_allowed,
        "intended_outputs": list(manifest.intended_outputs),
        "code_ref": manifest.code_ref,
        "environment_ref": manifest.environment_ref,
    }


@app.post("/secure-analysis/aggregates")
def restricted_aggregate_ingest(submission: AggregateResultSubmission) -> dict[str, object]:
    record = ingest_restricted_aggregate(submission)
    catalog.register_restricted_aggregate(record)
    return {
        "dataset_reference": record.dataset_reference.model_dump(mode="json"),
        "source_project_id": record.source_project_id,
        "restricted_dataset_name": record.restricted_dataset_name,
        "output_name": record.output_name,
        "manifest_hash": record.manifest_hash,
        "stored_raw_restricted_data": record.stored_raw_restricted_data,
        "disclosure_review": record.disclosure_review.model_dump(mode="json"),
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


@app.get("/atlas/admin/tier2")
def tier2_admin_dashboard(role: UserRole = "public") -> dict[str, object]:
    return {
        "role": role,
        "requests": [
            _tier2_payload(request) for request in catalog.tier2_requests_for_role(role)
        ],
    }


@app.post("/tier2/{canonical_dataset_name}/ingest")
def tier2_ingest(canonical_dataset_name: str, role: UserRole = "public") -> dict[str, object]:
    try:
        request = catalog.authorize_tier2_ingest(canonical_dataset_name, role=role)
    except AccessDeniedError as exc:
        return structured_error(exc)
    return {"status": "accepted", "request": _tier2_payload(request)}


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
