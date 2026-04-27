from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from fos_data_pipelines.models import ConnectorConfig, RawArtifact


@dataclass(frozen=True, slots=True)
class RawLandingResult:
    artifact: RawArtifact
    storage_path: Path


class RawZone:
    """Content-addressed raw landing zone for S3/MinIO-style object keys.

    Tests use a local filesystem root while production callers can map the same
    object keys onto an S3 or MinIO bucket. The raw key is deterministic and
    contains no source credentials.
    """

    def __init__(self, root: Path, uri_prefix: str = "s3://fos-raw") -> None:
        self.root = root
        self.uri_prefix = uri_prefix.rstrip("/")

    def object_key(self, config: ConnectorConfig, content_hash: str, filename: str) -> str:
        safe_name = Path(filename).name
        return (
            f"raw/{config.canonical_dataset_name}/dataset_version={config.dataset_version}/"
            f"connector={config.connector_name}/connector_version={config.connector_version}/"
            f"sha256={content_hash}/{safe_name}"
        )

    def land_file(self, source_path: Path, config: ConnectorConfig) -> RawLandingResult:
        content = source_path.read_bytes()
        content_hash = sha256(content).hexdigest()
        object_key = self.object_key(config, content_hash, source_path.name)
        storage_path = self.root / object_key
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not storage_path.exists():
            storage_path.write_bytes(content)
        artifact = RawArtifact(
            artifact_id=f"raw:{config.canonical_dataset_name}:{config.dataset_version}:{content_hash}",
            canonical_dataset_name=config.canonical_dataset_name,
            dataset_version=config.dataset_version,
            connector_name=config.connector_name,
            connector_version=config.connector_version,
            content_hash=content_hash,
            raw_uri=f"{self.uri_prefix}/{object_key}",
            byte_size=len(content),
        )
        return RawLandingResult(artifact=artifact, storage_path=storage_path)
