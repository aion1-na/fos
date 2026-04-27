from __future__ import annotations

import csv
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import ConnectorConfig, StagedArtifact

CONNECTOR_NAME = "gfs_osf_portal_fixture"
CONNECTOR_VERSION = "0.1.0"


def gfs_connector_config(source_uri: str = "osf+portal://registration-required/gfs-wave1") -> ConnectorConfig:
    return ConnectorConfig(
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name="gfs_wave1",
        dataset_version="fixture-0.1",
        access_mode="fixture",
        source_uri=source_uri,
        license_ref="docs/data/datasets/gfs-wave1.md#license-metadata",
        codebook_ref="codebooks/gfs_wave1.yaml",
        quality_profile_ref="docs/data/datasets/gfs-wave1.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/gfs-wave1.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/gfs-wave1.md#access-policy",
    )


def parse_gfs_wave1_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    rows = list(csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()))
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
    )
