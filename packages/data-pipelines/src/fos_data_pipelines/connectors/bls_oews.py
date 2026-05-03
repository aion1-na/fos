from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import ConnectorConfig, StagedArtifact

CONNECTOR_NAME = "bls_oews"
CONNECTOR_VERSION = "0.1.0"


def bls_oews_connector_config(source_uri: str) -> ConnectorConfig:
    return _bls_connector_config(
        connector_name=CONNECTOR_NAME,
        canonical_dataset_name="bls_oews",
        source_uri=source_uri,
        codebook_ref="codebooks/bls_oews.yaml",
        dataset_card="docs/data/datasets/bls-oews.md",
    )


def parse_bls_oews_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    rows = payload["Results"]["series"]
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=f"{CONNECTOR_NAME}_fixture_only",
        connector_version=CONNECTOR_VERSION,
    )


def _parse_bls_csv_fixture_only(
    fixture_path: Path,
    codebook_path: Path,
    output_dir: Path,
    connector_name: str,
) -> StagedArtifact:
    import csv

    codebook = load_codebook(codebook_path)
    rows = list(csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()))
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=f"{connector_name}_fixture_only",
        connector_version=CONNECTOR_VERSION,
    )


def _bls_connector_config(
    *,
    connector_name: str,
    canonical_dataset_name: str,
    source_uri: str,
    codebook_ref: str,
    dataset_card: str,
) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name=connector_name,
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name=canonical_dataset_name,
        dataset_version="request-status-v0.1",
        source_uri=source_uri,
        license_ref=f"{dataset_card}#license-metadata",
        codebook_ref=codebook_ref,
        quality_profile_ref=f"{dataset_card}#quality-profile",
        provenance_manifest_ref=f"{dataset_card}#provenance-manifest",
        access_policy_ref=f"{dataset_card}#access-policy",
    )


def bls_laus_connector_config(source_uri: str) -> ConnectorConfig:
    return _bls_connector_config(
        connector_name="bls_laus",
        canonical_dataset_name="bls_laus",
        source_uri=source_uri,
        codebook_ref="codebooks/bls_laus.yaml",
        dataset_card="docs/data/datasets/bls-laus.md",
    )


def bls_qcew_connector_config(source_uri: str) -> ConnectorConfig:
    return _bls_connector_config(
        connector_name="bls_qcew",
        canonical_dataset_name="bls_qcew",
        source_uri=source_uri,
        codebook_ref="codebooks/bls_qcew.yaml",
        dataset_card="docs/data/datasets/bls-qcew.md",
    )


def bls_employment_projections_connector_config(source_uri: str) -> ConnectorConfig:
    return _bls_connector_config(
        connector_name="bls_employment_projections",
        canonical_dataset_name="bls_employment_projections",
        source_uri=source_uri,
        codebook_ref="codebooks/bls_employment_projections.yaml",
        dataset_card="docs/data/datasets/bls-employment-projections.md",
    )


def parse_bls_laus_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_bls_csv_fixture_only(fixture_path, codebook_path, output_dir, "bls_laus")


def parse_bls_qcew_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_bls_csv_fixture_only(fixture_path, codebook_path, output_dir, "bls_qcew")


def parse_bls_employment_projections_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_bls_csv_fixture_only(
        fixture_path,
        codebook_path,
        output_dir,
        "bls_employment_projections",
    )
