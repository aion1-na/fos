from __future__ import annotations

from dataclasses import dataclass

from fos_data_pipelines.models import RawArtifact


@dataclass(frozen=True, slots=True)
class ArtifactLineage:
    artifact_id: str
    canonical_dataset_name: str
    dataset_version: str
    connector_name: str
    connector_version: str
    content_hash: str


class Catalog:
    def __init__(self) -> None:
        self.connector_versions: set[tuple[str, str]] = set()
        self.dataset_versions: set[tuple[str, str]] = set()
        self.artifacts: dict[str, ArtifactLineage] = {}

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
