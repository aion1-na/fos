from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccessMode(StrEnum):
    REQUEST_STATUS_STUB = "request_status_stub"
    FIXTURE = "fixture"
    APPROVED_PRODUCTION = "approved_production"


class DatasetReferenceModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    canonical_dataset_name: str = Field(min_length=1, pattern=r"^[a-z0-9_][a-z0-9_.-]*$")
    version: str = Field(min_length=1)
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.canonical_dataset_name, self.version, self.content_hash)


class ConnectorConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    connector_name: str = Field(min_length=1, pattern=r"^[a-z0-9_][a-z0-9_.-]*$")
    connector_version: str = Field(min_length=1)
    canonical_dataset_name: str = Field(min_length=1, pattern=r"^[a-z0-9_][a-z0-9_.-]*$")
    dataset_version: str = Field(min_length=1)
    access_mode: AccessMode = AccessMode.REQUEST_STATUS_STUB
    source_uri: str = Field(min_length=1)
    license_ref: str = Field(min_length=1)
    codebook_ref: str = Field(min_length=1)
    quality_profile_ref: str = Field(min_length=1)
    provenance_manifest_ref: str = Field(min_length=1)
    access_policy_ref: str = Field(min_length=1)

    @field_validator("source_uri")
    @classmethod
    def source_uri_must_not_embed_credentials(cls, value: str) -> str:
        lowered = value.lower()
        if "://" in value and "@" in value.split("://", 1)[1].split("/", 1)[0]:
            raise ValueError("source_uri must not embed credentials")
        secret_markers = ("pass" + "word=", "tok" + "en=", "api" + "_key=", "sec" + "ret=")
        if any(marker in lowered for marker in secret_markers):
            raise ValueError("source_uri must not contain secrets")
        return value


class RawArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    canonical_dataset_name: str
    dataset_version: str
    connector_name: str
    connector_version: str
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    raw_uri: str
    byte_size: int = Field(ge=0)
    landed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    media_type: str = "application/octet-stream"

    @property
    def dataset_reference(self) -> DatasetReferenceModel:
        return DatasetReferenceModel(
            canonical_dataset_name=self.canonical_dataset_name,
            version=self.dataset_version,
            content_hash=self.content_hash,
        )


class StagedArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    raw_artifact_id: str
    stage_uri: str
    schema_version: str
    row_count: int = Field(ge=0)
    transform_ref: str


class HarmonizedArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    artifact_id: str
    staged_artifact_id: str
    harmonized_uri: str
    schema_version: str
    codebook_mapping_ref: str
    quality_profile_ref: str


class FeatureTable(BaseModel):
    model_config = ConfigDict(frozen=True)

    table_id: str
    harmonized_artifact_id: str
    feature_table_uri: str
    schema_version: str
    dataset_reference: DatasetReferenceModel
    intended_use: Literal["simulation", "analysis", "metadata"]
