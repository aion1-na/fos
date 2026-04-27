from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fw_contracts import DatasetReference
from fos_data_pipelines.models import RawArtifact
from fos_data_pipelines.quality.cards import REQUIRED_CARD_FIELDS
from fos_data_service.admin_data import AdministrativeAggregateRecord
from fos_data_service.restricted_health import RestrictedMortalityAggregateRecord
from fos_data_service.secure_analysis import RestrictedAggregateRecord


@dataclass(frozen=True, slots=True)
class ArtifactLineage:
    artifact_id: str
    canonical_dataset_name: str
    dataset_version: str
    connector_name: str
    connector_version: str
    content_hash: str


@dataclass(frozen=True, slots=True)
class DatasetPolicyStatus:
    canonical_dataset_name: str
    tier: str
    status: str
    production_ready: bool
    missing_metadata: tuple[str, ...]

    @property
    def can_mark_production_ready(self) -> bool:
        return not self.missing_metadata and self.status == "approved_production"


AccessScope = Literal["public", "private"]
Tier2AccessStatus = Literal["request_status_stub", "pending", "approved", "rejected"]
Tier2LicenseStatus = Literal["not_approved", "pending", "approved", "rejected"]
UserRole = Literal["public", "admin", "secure_researcher"]


@dataclass(frozen=True, slots=True)
class AtlasAccessPolicy:
    canonical_dataset_name: str
    scope: AccessScope
    tier: str
    status: str
    limitations: str
    provenance_link: str
    gated_reason: str | None = None

    @property
    def is_public(self) -> bool:
        return self.scope == "public" and self.gated_reason is None


@dataclass(frozen=True, slots=True)
class Tier2AccessRequest:
    canonical_dataset_name: str
    owner: str
    submitted_on: str | None
    access_status: Tier2AccessStatus
    license_status: Tier2LicenseStatus
    secure_compartment: str
    requested_use: str
    updated_on: str

    @property
    def ingest_allowed(self) -> bool:
        return self.access_status == "approved" and self.license_status == "approved"


@dataclass(frozen=True, slots=True)
class DatasetRecord:
    reference: DatasetReference
    card_path: str
    manifest_path: str
    upstream_references: tuple[DatasetReference, ...] = ()
    consumed_by_runs: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()


class DataServiceError(Exception):
    code = "data_service_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class MissingDatasetError(DataServiceError):
    code = "missing_dataset"


class DatasetReferenceSchemaError(DataServiceError):
    code = "dataset_reference_schema_break"


class AccessDeniedError(DataServiceError):
    code = "access_denied"


class Catalog:
    def __init__(self) -> None:
        self.connector_versions: set[tuple[str, str]] = set()
        self.dataset_versions: set[tuple[str, str]] = set()
        self.artifacts: dict[str, ArtifactLineage] = {}
        self.dataset_policies: dict[str, DatasetPolicyStatus] = {}
        self.dataset_records: dict[tuple[str, str, str], DatasetRecord] = {}
        self.atlas_access_policies: dict[str, AtlasAccessPolicy] = {}
        self.tier2_access_requests: dict[str, Tier2AccessRequest] = {}
        self.restricted_aggregates: dict[tuple[str, str, str], RestrictedAggregateRecord] = {}
        self.administrative_aggregates: dict[
            tuple[str, str, str], AdministrativeAggregateRecord
        ] = {}
        self.restricted_mortality_aggregates: dict[
            tuple[str, str, str], RestrictedMortalityAggregateRecord
        ] = {}

    def register_connector_version(self, connector_name: str, connector_version: str) -> None:
        self.connector_versions.add((connector_name, connector_version))

    def register_dataset_version(self, canonical_dataset_name: str, dataset_version: str) -> None:
        self.dataset_versions.add((canonical_dataset_name, dataset_version))

    def register_raw_artifact(self, artifact: RawArtifact) -> ArtifactLineage:
        self.register_connector_version(artifact.connector_name, artifact.connector_version)
        self.register_dataset_version(artifact.canonical_dataset_name, artifact.dataset_version)
        lineage = ArtifactLineage(
            artifact_id=artifact.artifact_id,
            canonical_dataset_name=artifact.canonical_dataset_name,
            dataset_version=artifact.dataset_version,
            connector_name=artifact.connector_name,
            connector_version=artifact.connector_version,
            content_hash=artifact.content_hash,
        )
        self.artifacts[artifact.artifact_id] = lineage
        return lineage

    def artifact_lineage(self, artifact_id: str) -> ArtifactLineage | None:
        return self.artifacts.get(artifact_id)

    def register_dataset_policy(
        self,
        canonical_dataset_name: str,
        *,
        tier: str,
        status: str,
        production_ready: bool,
        metadata_fields: set[str],
    ) -> DatasetPolicyStatus:
        missing = tuple(field for field in REQUIRED_CARD_FIELDS if field not in metadata_fields)
        policy = DatasetPolicyStatus(
            canonical_dataset_name=canonical_dataset_name,
            tier=tier,
            status=status,
            production_ready=production_ready,
            missing_metadata=missing,
        )
        if production_ready and not policy.can_mark_production_ready:
            raise ValueError(
                f"{canonical_dataset_name} cannot be production-ready without approved access and complete metadata"
            )
        self.dataset_policies[canonical_dataset_name] = policy
        return policy

    def dataset_policy(self, canonical_dataset_name: str) -> DatasetPolicyStatus | None:
        return self.dataset_policies.get(canonical_dataset_name)

    def register_atlas_access_policy(self, policy: AtlasAccessPolicy) -> None:
        self.atlas_access_policies[policy.canonical_dataset_name] = policy

    def public_atlas_policies(self) -> list[AtlasAccessPolicy]:
        return [
            policy
            for policy in self.atlas_access_policies.values()
            if policy.is_public
        ]

    def private_atlas_policies(self) -> list[AtlasAccessPolicy]:
        return list(self.atlas_access_policies.values())

    def register_tier2_access_request(self, request: Tier2AccessRequest) -> None:
        self.tier2_access_requests[request.canonical_dataset_name] = request

    def tier2_requests_for_role(self, role: UserRole) -> list[Tier2AccessRequest]:
        if role == "public":
            return []
        return list(self.tier2_access_requests.values())

    def authorize_tier2_ingest(
        self,
        canonical_dataset_name: str,
        *,
        role: UserRole,
    ) -> Tier2AccessRequest:
        request = self.tier2_access_requests.get(canonical_dataset_name)
        if request is None:
            raise AccessDeniedError(f"{canonical_dataset_name} has no Tier 2 access request")
        if role != "secure_researcher":
            raise AccessDeniedError(f"{role} is not authorized for Tier 2 ingest")
        if not request.ingest_allowed:
            raise AccessDeniedError(
                f"{canonical_dataset_name} cannot be ingested before approved access and license"
            )
        return request

    def register_dataset_record(self, record: DatasetRecord) -> None:
        self.dataset_records[record.reference.as_tuple()] = record

    def resolve_dataset_reference(self, reference: DatasetReference) -> DatasetRecord:
        record = self.dataset_records.get(reference.as_tuple())
        if record is None:
            raise MissingDatasetError(
                f"dataset_reference {reference.as_tuple()} is not registered"
            )
        return record

    def register_restricted_aggregate(
        self,
        record: RestrictedAggregateRecord,
    ) -> RestrictedAggregateRecord:
        if record.stored_raw_restricted_data:
            raise AccessDeniedError("Tier 3 raw restricted data cannot be registered in FDW")
        if not record.disclosure_review.approved_for_fdw:
            raise AccessDeniedError("aggregate output lacks approved disclosure review")
        self.restricted_aggregates[record.dataset_reference.as_tuple()] = record
        return record

    def register_administrative_aggregate(
        self,
        record: AdministrativeAggregateRecord,
    ) -> AdministrativeAggregateRecord:
        if record.stored_row_level_data:
            raise AccessDeniedError("administrative row-level data cannot be registered in FDW")
        if record.disclosure_approval_status != "approved":
            raise AccessDeniedError("administrative aggregate lacks approved disclosure status")
        self.administrative_aggregates[record.dataset_reference.as_tuple()] = record
        return record

    def register_restricted_mortality_aggregate(
        self,
        record: RestrictedMortalityAggregateRecord,
    ) -> RestrictedMortalityAggregateRecord:
        if record.stored_raw_restricted_data:
            raise AccessDeniedError("restricted mortality raw data cannot be registered in FDW")
        if record.approval_status != "approved":
            raise AccessDeniedError("restricted mortality aggregate lacks approved status")
        self.restricted_mortality_aggregates[record.dataset_reference.as_tuple()] = record
        return record
