from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from fos_data_service.admin_data import (
    AdministrativeAggregateRecord,
    AdministrativeAggregateSubmission,
    AdministrativeDataAccess,
    ClaimsConnectorContract,
    HealthcareOutcomeMapping,
    ingest_administrative_aggregate,
)
from fos_data_service.app import (
    administrative_aggregate_ingest,
    administrative_data_dua_tracker,
    state_partnership_target_matrix,
    validate_claims_connector_contract,
)
from fos_data_service.catalog import AccessDeniedError, Catalog

ROOT = Path(__file__).resolve().parents[1]


def _approved_access(workflow: str = "state_ui") -> AdministrativeDataAccess:
    return AdministrativeDataAccess(
        source_name="state-ui-displacement" if workflow == "state_ui" else "claims-utilization",
        workflow=workflow,
        owner="State partnerships lead",
        license_status="approved",
        irb_status="approved",
        legal_status="approved",
        paid_license_status=None if workflow == "state_ui" else "approved",
        access_status="approved",
        next_action="Ingest approved aggregate calibration table.",
    )


def _claims_contract(license_status: str = "approved") -> ClaimsConnectorContract:
    return ClaimsConnectorContract(
        connector_name="claims_partner_contract_test",
        connector_version="0.1.0",
        vendor_or_steward="claims partner",
        license_status=license_status,
        paid_license_required=True,
        secret_free_contract_test=True,
        allowed_outputs=("healthcare_utilization",),
    )


def _submission(workflow: str = "state_ui") -> AdministrativeAggregateSubmission:
    return AdministrativeAggregateSubmission(
        access=_approved_access(workflow),
        connector=_claims_contract() if workflow == "claims" else None,
        aggregate_family="healthcare_utilization" if workflow == "claims" else "job_loss",
        output_name="state_ui_job_loss_rates_by_industry_region"
        if workflow == "state_ui"
        else "claims_ed_visit_rate_by_age_band",
        aggregate_payload={
            "artifact_kind": "approved_aggregate_calibration_table",
            "rows": [],
            "note": "Contract-test aggregate metadata only.",
        },
        disclosure_approval_status="approved",
        canonical_dataset_name="features.state_ui_admin_aggregates"
        if workflow == "state_ui"
        else "features.claims_utilization_aggregates",
        version="request-status-v0.1",
    )


def test_state_and_claims_workflows_require_license_irb_and_legal_signoff() -> None:
    pending = AdministrativeDataAccess(
        source_name="state-ui-displacement",
        workflow="state_ui",
        owner="State partnerships lead",
        license_status="approved",
        irb_status="pending",
        legal_status="approved",
        access_status="pending",
        next_action="Await IRB determination.",
    )
    with pytest.raises(ValidationError, match="license, IRB, and legal sign-off"):
        AdministrativeAggregateSubmission(
            **{**_submission().model_dump(), "access": pending.model_dump()}
        )


def test_paid_claims_license_is_not_assumed_available_without_status() -> None:
    contract = _claims_contract(license_status="request_status_stub")
    payload = validate_claims_connector_contract(contract)

    assert payload["license_status"] == "request_status_stub"
    assert payload["paid_license_required"] is True
    assert payload["secret_free_contract_test"] is True

    with pytest.raises(ValidationError, match="paid claims connector"):
        ClaimsConnectorContract(
            **{**contract.model_dump(), "secret_free_contract_test": False}
        )


def test_healthcare_taxonomy_maps_utilization_cautiously() -> None:
    mapping = HealthcareOutcomeMapping(
        source_outcome="emergency_department_visits",
        utilization_family="acute utilization",
        physical_health_domain_mapping="physical health stress proxy",
        confidence="cautious",
        caveat="Utilization reflects access and care-seeking behavior; calibration context only.",
    )

    assert mapping.confidence == "cautious"
    assert "proxy" in mapping.physical_health_domain_mapping

    with pytest.raises(ValidationError, match="must not overclaim"):
        HealthcareOutcomeMapping(
            source_outcome="inpatient_admissions",
            utilization_family="severe utilization",
            physical_health_domain_mapping="physical health",
            confidence="cautious",
            caveat="Treat as direct health score.",
        )


def test_approved_administrative_findings_return_as_aggregate_calibration_tables() -> None:
    record = ingest_administrative_aggregate(_submission())

    assert record.dataset_reference.canonical_dataset_name == "features.state_ui_admin_aggregates"
    assert record.dataset_reference.version == "request-status-v0.1"
    assert len(record.dataset_reference.content_hash) == 64
    assert record.aggregate_family == "job_loss"
    assert record.stored_row_level_data is False


def test_claims_aggregate_requires_contract_and_allowed_output() -> None:
    record = ingest_administrative_aggregate(_submission("claims"))

    assert record.dataset_reference.canonical_dataset_name == "features.claims_utilization_aggregates"
    assert record.workflow == "claims"
    assert record.aggregate_family == "healthcare_utilization"

    with pytest.raises(ValidationError, match="connector contract"):
        AdministrativeAggregateSubmission(
            **{**_submission("claims").model_dump(), "connector": None}
        )


def test_catalog_rejects_unapproved_or_row_level_admin_data() -> None:
    catalog = Catalog()
    record = ingest_administrative_aggregate(_submission())
    bad_status = AdministrativeAggregateRecord(
        **{**record.model_dump(), "disclosure_approval_status": "pending"}
    )
    bad_row_level = AdministrativeAggregateRecord(
        **{**record.model_dump(), "stored_row_level_data": True}
    )

    with pytest.raises(AccessDeniedError, match="approved disclosure"):
        catalog.register_administrative_aggregate(bad_status)
    with pytest.raises(AccessDeniedError, match="row-level data"):
        catalog.register_administrative_aggregate(bad_row_level)


def test_data_service_endpoints_expose_request_status_and_ingest_approved_aggregate() -> None:
    targets = state_partnership_target_matrix()["targets"]
    dua = administrative_data_dua_tracker()["sources"]
    payload = administrative_aggregate_ingest(_submission())

    assert targets[0]["license_status"] == "request_status_stub"
    assert dua[1]["paid_license_status"] == "request_status_stub"
    assert dua[1]["ingest_allowed"] is False
    assert payload["dataset_reference"]["canonical_dataset_name"] == (
        "features.state_ui_admin_aggregates"
    )
    assert payload["stored_row_level_data"] is False


def test_admin_data_docs_and_dataset_cards_capture_required_boundaries() -> None:
    docs = [
        ROOT / "docs/data/admin/state-partnership-target-matrix.md",
        ROOT / "docs/data/admin/administrative-data-dua-tracker.md",
        ROOT / "docs/data/admin/claims-connector-contract.md",
        ROOT / "docs/data/admin/healthcare-utilization-outcome-taxonomy.md",
        ROOT / "docs/data/admin/state-ui-displacement-analysis-plan.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)

    assert "No state administrative data is assumed available" in combined
    assert "license, IRB, and legal sign-off before ingestion" in combined
    assert "Paid claims data is not assumed available" in combined
    assert "not treated as a direct health score" in combined
    assert "approved aggregate calibration tables" in combined

    for slug in ["state-ui-admin-aggregates", "claims-utilization-aggregates"]:
        card = (ROOT / "docs/data/datasets" / f"{slug}.md").read_text(encoding="utf-8")
        for required in [
            "License metadata:",
            "Codebook mapping:",
            "Quality profile:",
            "Provenance manifest:",
            "Access policy:",
        ]:
            assert required in card
