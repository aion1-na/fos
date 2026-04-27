from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from fw_contracts import DatasetReference

RESTRICTED_MORTALITY_MIN_CELL_COUNT = 10
ALLOWED_ATLAS_GEOGRAPHIES = frozenset({"national", "state", "region"})
PROHIBITED_ATLAS_GEOGRAPHIES = frozenset({"county", "tract", "zip", "block_group"})
ALLOWED_DEMOGRAPHIC_FIELDS = frozenset({"age_band", "sex", "cause_group"})
PROHIBITED_DEMOGRAPHIC_FIELDS = frozenset(
    {"race_ethnicity_detail", "single_year_age", "exact_birth_year"}
)

ApprovalStatus = Literal["request_status_stub", "pending_disclosure_review", "approved", "rejected"]
HealthSourceEnvironment = Literal["nchs_rdc", "state_vital_statistics", "cdc_wonder_public"]


class SourceEnvironmentMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    environment: HealthSourceEnvironment
    steward: str = Field(min_length=1)
    access_status: Literal["request_status_stub", "approved", "rejected"]
    disclosure_protocol: str = Field(min_length=1)
    public_cdc_wonder_output: bool = False


class MortalityAggregateRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    geography_level: str = Field(min_length=1)
    geography_label: str = Field(min_length=1)
    demographic_fields: tuple[str, ...]
    cause_group: str = Field(min_length=1)
    deaths: int | None = None
    mortality_rate: float | None = None
    suppressed: bool
    suppression_rule: str = Field(min_length=1)

    @model_validator(mode="after")
    def enforce_disclosure_constraints(self) -> "MortalityAggregateRow":
        if self.geography_level in PROHIBITED_ATLAS_GEOGRAPHIES:
            raise ValueError(f"{self.geography_level} geography is prohibited in Atlas")
        prohibited_fields = PROHIBITED_DEMOGRAPHIC_FIELDS.intersection(self.demographic_fields)
        if prohibited_fields:
            raise ValueError(f"prohibited demographic detail: {sorted(prohibited_fields)}")
        if not set(self.demographic_fields).issubset(ALLOWED_DEMOGRAPHIC_FIELDS):
            raise ValueError("demographic fields must be Atlas-safe aggregate fields")
        if self.suppressed:
            if self.deaths is not None or self.mortality_rate is not None:
                raise ValueError("suppressed mortality rows cannot expose deaths or rate")
        elif self.deaths is None or self.deaths < RESTRICTED_MORTALITY_MIN_CELL_COUNT:
            raise ValueError("unsuppressed mortality rows must meet small-cell threshold")
        return self


class RestrictedMortalityAggregateSubmission(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_environment: SourceEnvironmentMetadata
    approval_status: ApprovalStatus
    review_id: str = Field(min_length=1)
    canonical_dataset_name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    rows: tuple[MortalityAggregateRow, ...]
    intended_use: str = Field(min_length=1)

    @model_validator(mode="after")
    def separate_restricted_from_public_cdc_wonder(
        self,
    ) -> "RestrictedMortalityAggregateSubmission":
        if self.source_environment.public_cdc_wonder_output:
            raise ValueError("restricted mortality path cannot ingest public CDC WONDER outputs")
        if self.source_environment.environment == "cdc_wonder_public":
            raise ValueError("restricted health outputs must stay separate from CDC WONDER public")
        if self.approval_status != "approved":
            raise ValueError("restricted mortality aggregate requires approved disclosure status")
        if not self.rows:
            raise ValueError("restricted mortality aggregate requires at least one row")
        return self


class RestrictedMortalityAggregateRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_reference: DatasetReference
    source_environment: SourceEnvironmentMetadata
    approval_status: ApprovalStatus
    review_id: str
    atlas_safe_rows: tuple[MortalityAggregateRow, ...]
    stored_raw_restricted_data: bool = False


def _stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def ingest_restricted_mortality_aggregate(
    submission: RestrictedMortalityAggregateSubmission,
) -> RestrictedMortalityAggregateRecord:
    content_hash = _stable_hash(
        {
            "approval_status": submission.approval_status,
            "review_id": submission.review_id,
            "rows": [row.model_dump(mode="json") for row in submission.rows],
            "source_environment": submission.source_environment.model_dump(mode="json"),
        }
    )
    return RestrictedMortalityAggregateRecord(
        dataset_reference=DatasetReference(
            canonical_dataset_name=submission.canonical_dataset_name,
            version=submission.version,
            content_hash=content_hash,
        ),
        source_environment=submission.source_environment,
        approval_status=submission.approval_status,
        review_id=submission.review_id,
        atlas_safe_rows=submission.rows,
    )
