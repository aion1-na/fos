from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import StagedArtifact

CONNECTOR_NAME = "bls_oews_api_fixture"
CONNECTOR_VERSION = "0.1.0"


def parse_bls_oews_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    codebook = load_codebook(codebook_path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    rows = payload["Results"]["series"]
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
    )
