from __future__ import annotations

import csv
import json
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import StagedArtifact

CONNECTOR_VERSION = "0.1.0"


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
    return _parse_exposure_csv(fixture_path, codebook_path, output_dir, "eloundou_fixture")


def parse_felten_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    return _parse_exposure_csv(fixture_path, codebook_path, output_dir, "felten_fixture")


def parse_webb_request_status_stub(fixture_path: Path) -> dict[str, object]:
    return json.loads(fixture_path.read_text(encoding="utf-8"))


def parse_anthropic_economic_index_request_status_stub(fixture_path: Path) -> dict[str, object]:
    return json.loads(fixture_path.read_text(encoding="utf-8"))
