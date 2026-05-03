from __future__ import annotations

import csv
import json
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import ConnectorConfig, StagedArtifact

CONNECTOR_VERSION = "0.1.0"


def ai_exposure_connector_config(
    *,
    connector_name: str,
    canonical_dataset_name: str,
    source_uri: str,
    dataset_card: str,
    dataset_version: str = "request-status-v0.1",
) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name=connector_name,
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name=canonical_dataset_name,
        dataset_version=dataset_version,
        source_uri=source_uri,
        license_ref=f"{dataset_card}#license-metadata",
        codebook_ref="codebooks/ai_exposure_measures.yaml",
        quality_profile_ref=f"{dataset_card}#quality-profile",
        provenance_manifest_ref=f"{dataset_card}#provenance-manifest",
        access_policy_ref=f"{dataset_card}#access-policy",
    )


def _parse_exposure_csv(
    fixture_path: Path,
    codebook_path: Path,
    output_dir: Path,
    connector_name: str,
) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    rows = list(csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()))
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=connector_name,
        connector_version=CONNECTOR_VERSION,
    )


def parse_eloundou_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    return _parse_exposure_csv(fixture_path, codebook_path, output_dir, "eloundou_fixture_only")


def parse_eloundou_public_archive(
    archive_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_exposure_csv(archive_path, codebook_path, output_dir, "eloundou_public_archive")


def parse_felten_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    return _parse_exposure_csv(fixture_path, codebook_path, output_dir, "felten_fixture_only")


def parse_felten_public_archive(
    archive_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_exposure_csv(archive_path, codebook_path, output_dir, "felten_public_archive")


def parse_acemoglu_restrepo_robot_fixture_only(
    fixture_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_exposure_csv(
        fixture_path,
        codebook_path,
        output_dir,
        "acemoglu_restrepo_robot_fixture_only",
    )


def parse_acemoglu_restrepo_robot_public_archive(
    archive_path: Path, codebook_path: Path, output_dir: Path
) -> StagedArtifact:
    return _parse_exposure_csv(
        archive_path,
        codebook_path,
        output_dir,
        "acemoglu_restrepo_robot_public_archive",
    )


def parse_webb_request_status_stub(fixture_path: Path) -> dict[str, object]:
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def parse_anthropic_economic_index_request_status_stub(fixture_path: Path) -> dict[str, object]:
    return json.loads(fixture_path.read_text(encoding="utf-8"))
