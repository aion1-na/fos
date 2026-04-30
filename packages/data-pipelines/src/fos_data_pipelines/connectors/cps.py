from __future__ import annotations

import csv
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import ConnectorConfig, StagedArtifact

CONNECTOR_NAME = "cps_young_adults"
CONNECTOR_VERSION = "0.1.0"


def cps_young_adult_connector_config(source_uri: str) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name="cps_young_adults",
        dataset_version="request-status-v0.1",
        source_uri=source_uri,
        license_ref="docs/data/datasets/cps-young-adults.md#license-metadata",
        codebook_ref="codebooks/cps_person.yaml",
        quality_profile_ref="docs/data/datasets/cps-young-adults.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/cps-young-adults.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/cps-young-adults.md#access-policy",
    )


def cps_labor_context_connector_config(source_uri: str) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name="cps_labor_context",
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name="cps_labor_context",
        dataset_version="request-status-v0.1",
        source_uri=source_uri,
        license_ref="docs/data/datasets/cps-labor-context.md#license-metadata",
        codebook_ref="codebooks/cps_labor_context.yaml",
        quality_profile_ref="docs/data/datasets/cps-labor-context.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/cps-labor-context.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/cps-labor-context.md#access-policy",
    )


def parse_cps_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    rows = list(csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()))
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=f"{CONNECTOR_NAME}_fixture_only",
        connector_version=CONNECTOR_VERSION,
    )


def parse_cps_labor_context_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    rows = list(csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()))
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name="cps_labor_context_fixture_only",
        connector_version=CONNECTOR_VERSION,
    )
