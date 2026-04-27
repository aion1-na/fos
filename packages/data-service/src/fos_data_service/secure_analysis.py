from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from fw_contracts import DatasetReference

AccessStatus = Literal["request_status_stub", "approved", "rejected"]
DisclosureStatus = Literal["pending", "approved", "rejected"]
SecureEnvironment = Literal["census_rdc", "external_secure_enclave", "provider_clean_room"]


class SecureAnalysisManifest(BaseModel):
    model_config = ConfigDict(frozen=True)

    project_id: str = Field(min_length=1)
    environment: SecureEnvironment
    restricted_dataset_name: str = Field(min_length=1)
    access_status: AccessStatus
    raw_restricted_data_in_fdw_allowed: bool = False
    raw_restricted_data_uri: str | None = None
    code_ref: str = Field(min_length=1)
    code_hash: str = Field(min_length=64, max_length=64)
    environment_ref: str = Field(min_length=1)
    environment_hash: str = Field(min_length=64, max_length=64)
    intended_outputs: tuple[str, ...]
    owner: str = Field(min_length=1)
    timeline: str = Field(min_length=1)

    @model_validator(mode="after")
    def restricted_raw_data_cannot_enter_fdw(self) -> "SecureAnalysisManifest":
        if self.raw_restricted_data_uri and not self.raw_restricted_data_in_fdw_allowed:
            raise ValueError("Tier 3 raw restricted data cannot be stored in FDW")
        if not self.intended_outputs:
            raise ValueError("RDC analysis packs must declare intended outputs")
        return self


class DisclosureReview(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: DisclosureStatus
    reviewed_by: str = Field(min_length=1)
    reviewed_on: str = Field(min_length=1)
    cell_suppression_checked: bool
    reidentification_risk_checked: bool
    publication_allowed: bool
    notes: str = Field(min_length=1)

    @property
    def approved_for_fdw(self) -> bool:
        return (
            self.status == "approved"
            and self.cell_suppression_checked
            and self.reidentification_risk_checked
            and self.publication_allowed
        )


class AggregateResultSubmission(BaseModel):
    model_config = ConfigDict(frozen=True)

    manifest: SecureAnalysisManifest
    output_name: str = Field(min_length=1)
    output_level: Literal["aggregate"]
    aggregate_payload: dict[str, object]
    disclosure_review: DisclosureReview
    canonical_dataset_name: str = Field(min_length=1)
    version: str = Field(min_length=1)

    @model_validator(mode="after")
    def only_approved_aggregates_enter_fdw(self) -> "AggregateResultSubmission":
        if self.output_name not in self.manifest.intended_outputs:
            raise ValueError("aggregate output was not declared in the analysis manifest")
        if self.output_level != "aggregate":
            raise ValueError("only aggregate outputs may be submitted to FDW")
        if not self.disclosure_review.approved_for_fdw:
            raise ValueError("aggregate output lacks approved disclosure review")
        return self


class RestrictedAggregateRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_reference: DatasetReference
    source_project_id: str
    restricted_dataset_name: str
    output_name: str
    disclosure_review: DisclosureReview
    manifest_hash: str
    stored_raw_restricted_data: bool = False


def _stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def ingest_restricted_aggregate(submission: AggregateResultSubmission) -> RestrictedAggregateRecord:
    manifest_payload = submission.manifest.model_dump(mode="json")
    manifest_hash = _stable_hash(manifest_payload)
    content_hash = _stable_hash(
        {
            "aggregate_payload": submission.aggregate_payload,
            "disclosure_review": submission.disclosure_review.model_dump(mode="json"),
            "manifest_hash": manifest_hash,
            "output_name": submission.output_name,
        }
    )
    reference = DatasetReference(
        canonical_dataset_name=submission.canonical_dataset_name,
        version=submission.version,
        content_hash=content_hash,
    )
    return RestrictedAggregateRecord(
        dataset_reference=reference,
        source_project_id=submission.manifest.project_id,
        restricted_dataset_name=submission.manifest.restricted_dataset_name,
        output_name=submission.output_name,
        disclosure_review=submission.disclosure_review,
        manifest_hash=manifest_hash,
    )
