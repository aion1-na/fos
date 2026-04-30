from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.connectors import (
    brfss_public_connector_config,
    cdc_wonder_connector_config,
)
from fos_data_pipelines.health_public.context import (
    CELL_SUPPRESSION_THRESHOLD,
    build_health_validation_context,
    parse_public_health_stub,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "health_public"


def test_mortality_outputs_respect_public_use_cell_suppression(tmp_path: Path) -> None:
    output_path, reference = build_health_validation_context(
        FIXTURES / "cdc_mortality_fixture.csv",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()

    suppressed = [row for row in rows if row["suppressed"]]
    visible = [row for row in rows if not row["suppressed"]]
    assert reference.canonical_dataset_name == "features.health_validation_context"
    assert CELL_SUPPRESSION_THRESHOLD == 10
    assert suppressed[0]["deaths"] is None
    assert suppressed[0]["mortality_rate"] is None
    assert visible[0]["deaths"] == 24
    assert visible[0]["country_iso3"] == "USA"
    assert all(len(row["content_hash"]) == 64 for row in rows)
    assert {row["codebook_version"] for row in rows} == {"0.1"}
    assert all(row["dataset_reference"].startswith("(features.health_validation_context") for row in rows)


def test_public_health_connectors_are_request_status_for_governed_sources() -> None:
    for name in [
        "brfss_public_stub.json",
        "nhis_public_stub.json",
        "nhanes_public_stub.json",
        "meps_public_stub.json",
    ]:
        stub = parse_public_health_stub(FIXTURES / name)
        assert stub["access_status"] == "request_status_stub"
        assert stub["public_table_status"] == "public where published"
        assert "microdata" in str(stub["microdata_status"])


def test_health_data_cards_document_public_table_microdata_limitations() -> None:
    for slug in ["cdc-public-health", "brfss-public", "nhis-public", "nhanes-public", "meps-public"]:
        card = (ROOT / "docs" / "data" / "datasets" / f"{slug}.md").read_text(encoding="utf-8")
        assert "public table" in card.lower()
        assert "microdata" in card.lower()
        assert "Access policy:" in card


def test_public_health_connector_configs_have_metadata_refs() -> None:
    for config in [
        brfss_public_connector_config("https://example.org/brfss"),
        cdc_wonder_connector_config("https://example.org/cdc-wonder"),
    ]:
        assert config.dataset_version == "request-status-v0.1"
        assert (ROOT / config.codebook_ref).exists()
        assert (ROOT / config.license_ref.split("#", 1)[0]).exists()
