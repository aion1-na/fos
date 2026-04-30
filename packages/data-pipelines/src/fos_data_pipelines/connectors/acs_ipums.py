from __future__ import annotations

import csv
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import ConnectorConfig, StagedArtifact


CONNECTOR_NAME = "acs_ipums_fixture"
CONNECTOR_VERSION = "0.1.0"


def acs_pums_young_adult_connector_config(source_uri: str) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name="acs_pums_young_adults",
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name="acs_pums_young_adults",
        dataset_version="request-status-v0.1",
        source_uri=source_uri,
        license_ref="docs/data/datasets/acs-ipums.md#license-metadata",
        codebook_ref="codebooks/acs_person.yaml, codebooks/acs_household.yaml",
        quality_profile_ref="docs/data/datasets/acs-ipums.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/acs-ipums.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/acs-ipums.md#access-policy",
    )


def parse_acs_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
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
