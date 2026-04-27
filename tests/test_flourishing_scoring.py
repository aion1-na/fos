from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.connectors.cross_validation import (
    parse_ess_stub,
    parse_world_happiness_report_stub,
    parse_wvs_stub,
)
from fos_data_pipelines.connectors.gfs import gfs_connector_config, parse_gfs_wave1_fixture
from fos_data_pipelines.scoring.flourishing import (
    DOMAIN_FIELDS,
    build_gfs_wave1_marginals,
    score_six_domain_country_marginals,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures"
GFS_FIXTURE = FIXTURES / "gfs" / "wave1_fixture.csv"
CODEBOOK = ROOT / "codebooks" / "gfs_wave1.yaml"


def test_gfs_connector_uses_registration_gated_portal_metadata() -> None:
    config = gfs_connector_config()

    assert config.canonical_dataset_name == "gfs_wave1"
    assert config.source_uri == "osf+portal://registration-required/gfs-wave1"
    assert config.license_ref == "docs/data/datasets/gfs-wave1.md#license-metadata"
    assert config.codebook_ref == "codebooks/gfs_wave1.yaml"


def test_gfs_fixture_parses_to_staged_parquet(tmp_path: Path) -> None:
    artifact = parse_gfs_wave1_fixture(GFS_FIXTURE, CODEBOOK, tmp_path)
    table = pq.read_table(Path(artifact.stage_uri.removeprefix("file://")))

    assert artifact.row_count == 4
    assert set(DOMAIN_FIELDS).issubset(set(table.column_names))
    assert "sampling_weight" in table.column_names


def test_six_domain_scoring_matches_reference_outputs() -> None:
    expected = json.loads((FIXTURES / "gfs" / "reference_scores.json").read_text(encoding="utf-8"))
    actual = score_six_domain_country_marginals(GFS_FIXTURE)

    assert actual == expected


def test_gfs_wave1_country_marginals_emit_feature_dataset_references(tmp_path: Path) -> None:
    outputs = build_gfs_wave1_marginals(GFS_FIXTURE, tmp_path)

    assert set(outputs) == {"JP", "US"}
    for country, (path, reference) in outputs.items():
        rows = pq.read_table(path).to_pylist()
        assert reference.canonical_dataset_name == (
            f"features.gfs_wave1_marginals_country_{country.lower()}"
        )
        assert reference.version == "fixture-0.1"
        assert len(reference.content_hash) == 64
        assert {row["domain"] for row in rows} == set(DOMAIN_FIELDS)
        assert all(row["sampling_weighted"] is True for row in rows)
        assert all(row["measurement_mode"] == "cross_sectional_research_grade" for row in rows)


def test_cross_validation_connectors_are_request_status_stubs() -> None:
    whr = parse_world_happiness_report_stub(
        FIXTURES / "cross_validation" / "world_happiness_report_stub.json"
    )
    ess = parse_ess_stub(FIXTURES / "cross_validation" / "ess_stub.json")
    wvs = parse_wvs_stub(FIXTURES / "cross_validation" / "wvs_stub.json")

    assert whr["access_status"] == "request_status_stub"
    assert ess["access_status"] == "request_status_stub"
    assert wvs["access_status"] == "request_status_stub"
    assert whr["rows"] == []


def test_gfs_card_contains_sampling_weights_limitations_and_citation() -> None:
    card = (ROOT / "docs" / "data" / "datasets" / "gfs-wave1.md").read_text(encoding="utf-8")

    assert "Sampling design:" in card
    assert "Weights:" in card
    assert "Limitations:" in card
    assert "Citation instructions:" in card
    assert "cross-sectional" in card
    assert "prospective forecasting" in card


def test_advisor_review_queue_for_gfs_codebook_is_populated() -> None:
    queue = (ROOT / "docs" / "data" / "review" / "gfs-codebook-queue.md").read_text(
        encoding="utf-8"
    )

    assert "Confirm six-domain item wording" in queue
    assert "Confirm sampling weight interpretation" in queue
    assert "Pending" in queue
