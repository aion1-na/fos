from __future__ import annotations

from dataclasses import dataclass

from fw_contracts import DatasetReference
from fos_data_pipelines.models import RawArtifact
from fos_data_pipelines.quality.cards import REQUIRED_CARD_FIELDS


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


class Catalog:
    def __init__(self) -> None:
        self.connector_versions: set[tuple[str, str]] = set()
        self.dataset_versions: set[tuple[str, str]] = set()
        self.artifacts: dict[str, ArtifactLineage] = {}
        self.dataset_policies: dict[str, DatasetPolicyStatus] = {}
        self.dataset_records: dict[tuple[str, str, str], DatasetRecord] = {}

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

    def register_dataset_record(self, record: DatasetRecord) -> None:
        self.dataset_records[record.reference.as_tuple()] = record

    def resolve_dataset_reference(self, reference: DatasetReference) -> DatasetRecord:
        record = self.dataset_records.get(reference.as_tuple())
        if record is None:
            raise MissingDatasetError(
                f"dataset_reference {reference.as_tuple()} is not registered"
            )
        return record
