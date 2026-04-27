from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from fw_contracts import DatasetReference

ApprovalStatus = Literal["request_status_stub", "pending", "approved", "rejected"]
WorkflowKind = Literal["state_ui", "claims"]
AggregateFamily = Literal[
    "job_loss",
    "reemployment",
    "wage_trajectory",
    "healthcare_utilization",
]
OutcomeConfidence = Literal["cautious", "exploratory", "not_supported"]


class AdministrativeDataAccess(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_name: str = Field(min_length=1)
    workflow: WorkflowKind
    owner: str = Field(min_length=1)
    license_status: ApprovalStatus
    irb_status: ApprovalStatus
    legal_status: ApprovalStatus
    paid_license_status: ApprovalStatus | None = None
    access_status: ApprovalStatus = "request_status_stub"
    next_action: str = Field(min_length=1)

    @property
    def ingest_allowed(self) -> bool:
        approvals = (self.license_status, self.irb_status, self.legal_status)
        paid_license_ok = self.paid_license_status in (None, "approved")
        return all(status == "approved" for status in approvals) and paid_license_ok


class ClaimsConnectorContract(BaseModel):
    model_config = ConfigDict(frozen=True)

    connector_name: str = Field(min_length=1)
    connector_version: str = Field(min_length=1)
    vendor_or_steward: str = Field(min_length=1)
    workflow: Literal["claims"] = "claims"
    license_status: ApprovalStatus
    paid_license_required: bool
    secret_free_contract_test: bool
    allowed_outputs: tuple[AggregateFamily, ...]
    credential_fields: tuple[str, ...] = ()

    @model_validator(mode="after")
    def no_paid_license_assumed_without_status(self) -> "ClaimsConnectorContract":
        if self.paid_license_required and self.license_status != "approved":
            if not self.secret_free_contract_test:
                raise ValueError("paid claims connector requires approved license or contract test")
        if any("secret" in field.lower() or "token" in field.lower() for field in self.credential_fields):
            raise ValueError("real credential fields are not allowed in source-controlled contracts")
        if not self.allowed_outputs:
            raise ValueError("claims connector must declare allowed aggregate outputs")
        return self


class HealthcareOutcomeMapping(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_outcome: str = Field(min_length=1)
    utilization_family: str = Field(min_length=1)
    physical_health_domain_mapping: str = Field(min_length=1)
    confidence: OutcomeConfidence
    caveat: str = Field(min_length=1)

    @model_validator(mode="after")
    def utilization_mapping_must_be_cautious(self) -> "HealthcareOutcomeMapping":
        if self.confidence == "not_supported":
            return self
        if "causal" in self.caveat.lower() or "direct health score" in self.caveat.lower():
            raise ValueError("utilization taxonomy must not overclaim health-domain meaning")
        return self


class AdministrativeAggregateSubmission(BaseModel):
    model_config = ConfigDict(frozen=True)

    access: AdministrativeDataAccess
    connector: ClaimsConnectorContract | None = None
    aggregate_family: AggregateFamily
    output_name: str = Field(min_length=1)
    aggregate_payload: dict[str, object]
    disclosure_approval_status: ApprovalStatus
    canonical_dataset_name: str = Field(min_length=1)
    version: str = Field(min_length=1)

    @model_validator(mode="after")
    def require_full_approval_before_ingestion(self) -> "AdministrativeAggregateSubmission":
        if not self.access.ingest_allowed:
            raise ValueError("license, IRB, and legal sign-off are required before ingestion")
        if self.disclosure_approval_status != "approved":
            raise ValueError("aggregate calibration table requires approved disclosure status")
        if self.access.workflow == "claims":
            if self.connector is None:
                raise ValueError("claims aggregate requires a claims connector contract")
            if self.aggregate_family not in self.connector.allowed_outputs:
                raise ValueError("aggregate family is not allowed by connector contract")
        if not self.aggregate_payload:
            raise ValueError("aggregate payload must be an approved aggregate table")
        return self


class AdministrativeAggregateRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_reference: DatasetReference
    source_name: str
    workflow: WorkflowKind
    aggregate_family: AggregateFamily
    output_name: str
    disclosure_approval_status: ApprovalStatus
    stored_row_level_data: bool = False


def _stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def ingest_administrative_aggregate(
    submission: AdministrativeAggregateSubmission,
) -> AdministrativeAggregateRecord:
    content_hash = _stable_hash(
        {
            "access": submission.access.model_dump(mode="json"),
            "aggregate_family": submission.aggregate_family,
            "aggregate_payload": submission.aggregate_payload,
            "connector": submission.connector.model_dump(mode="json") if submission.connector else None,
            "disclosure_approval_status": submission.disclosure_approval_status,
            "output_name": submission.output_name,
        }
    )
    return AdministrativeAggregateRecord(
        dataset_reference=DatasetReference(
            canonical_dataset_name=submission.canonical_dataset_name,
            version=submission.version,
            content_hash=content_hash,
        ),
        source_name=submission.access.source_name,
        workflow=submission.access.workflow,
        aggregate_family=submission.aggregate_family,
        output_name=submission.output_name,
        disclosure_approval_status=submission.disclosure_approval_status,
    )
