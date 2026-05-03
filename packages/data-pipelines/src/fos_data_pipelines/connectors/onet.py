from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import ConnectorConfig, StagedArtifact

CONNECTOR_NAME = "onet_api_fixture_only"
CONNECTOR_VERSION = "0.1.0"


def onet_connector_config(source_uri: str) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name="onet",
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name="onet",
        dataset_version="request-status-v0.1",
        source_uri=source_uri,
        license_ref="docs/data/datasets/onet.md#license-metadata",
        codebook_ref="codebooks/onet.yaml",
        quality_profile_ref="docs/data/datasets/onet.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/onet.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/onet.md#access-policy",
    )


def parse_onet_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    rows = json.loads(fixture_path.read_text(encoding="utf-8"))
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
    )
