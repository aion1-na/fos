from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from fos_data_pipelines.connectors.cross_validation import (
    parse_ess_stub,
    parse_world_happiness_report_stub,
    parse_wvs_stub,
)
from fos_data_pipelines.connectors.gfs import (
    SensitiveDataAccessError,
    acquire_gfs_non_sensitive_source,
    build_gfs_request_status_stub,
    gfs_connector_config,
    parse_gfs_wave1_fixture,
)
from fos_data_pipelines.scoring.flourishing import (
    DOMAIN_FIELDS,
    build_gfs_wave12_marginals_country,
    build_gfs_wave12_panel_non_sensitive,
    build_gfs_wave1_marginals,
    score_flourishing_row,
    score_six_domain_country_marginals,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures"
GFS_FIXTURE = FIXTURES / "gfs" / "wave1_fixture.csv"
GFS_WAVE1_PANEL_FIXTURE = FIXTURES / "gfs" / "wave1_panel_fixture_only.csv"
GFS_WAVE2_PANEL_FIXTURE = FIXTURES / "gfs" / "wave2_panel_fixture_only.csv"
GFS_SENSITIVE_FIXTURE = FIXTURES / "gfs" / "wave1_sensitive_fixture_only.csv"
CODEBOOK = ROOT / "codebooks" / "gfs_wave1.yaml"


def test_gfs_connector_uses_registration_gated_portal_metadata() -> None:
    config = gfs_connector_config()

    assert config.canonical_dataset_name == "gfs_wave1"
    assert config.source_uri == "osf+cos://registration-required/gfs-wave1/non-sensitive"
    assert config.access_mode == "request_status_stub"
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


def test_gfs_connector_detects_available_non_sensitive_source() -> None:
    config = gfs_connector_config(str(GFS_WAVE1_PANEL_FIXTURE), wave=1)

    assert config.access_mode == "fixture"
    assert config.dataset_version == "fixture-0.1"


def test_gfs_connector_requires_access_approval_for_local_production_source(tmp_path: Path) -> None:
    source = tmp_path / "gfs_wave1_non_sensitive.csv"
    source.write_text(GFS_WAVE1_PANEL_FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

    pending = gfs_connector_config(str(source), wave=1)
    assert pending.access_mode == "request_status_stub"

    source.with_suffix(source.suffix + ".access-approved.json").write_text(
        '{"approved_by":"unit-test","scope":"non-sensitive"}\n',
        encoding="utf-8",
    )
    approved = gfs_connector_config(str(source), wave=1)
    acquired = acquire_gfs_non_sensitive_source(approved)

    assert approved.access_mode == "approved_production"
    assert acquired["row_count"] == 4
    assert acquired["dataset_reference"]["canonical_dataset_name"] == "gfs_wave1"


def test_sensitive_gfs_fields_are_blocked_without_approved_policy(tmp_path: Path) -> None:
    with pytest.raises(SensitiveDataAccessError):
        parse_gfs_wave1_fixture(GFS_SENSITIVE_FIXTURE, CODEBOOK, tmp_path)

    with pytest.raises(SensitiveDataAccessError):
        build_gfs_wave12_panel_non_sensitive([GFS_SENSITIVE_FIXTURE], tmp_path)


def test_flourishing_scoring_kernel_scores_10_and_12_item_indices() -> None:
    row = {
        "happiness_1": 8,
        "happiness_2": 6,
        "health_1": 7,
        "health_2": 7,
        "meaning_1": 6,
        "meaning_2": 8,
        "character_1": 9,
        "character_2": 7,
        "relationships_1": 5,
        "relationships_2": 7,
        "financial_1": 4,
        "financial_2": 6,
    }

    scores = score_flourishing_row(row)

    assert scores["happiness"] == 7
    assert scores["flourish_index_10"] == 7
    assert scores["secure_flourish_index_12"] == pytest.approx(6.666667, abs=0.000001)


def test_gfs_wave12_panel_and_country_marginals_emit_dataset_references(tmp_path: Path) -> None:
    panel_path, panel_reference = build_gfs_wave12_panel_non_sensitive(
        [GFS_WAVE1_PANEL_FIXTURE, GFS_WAVE2_PANEL_FIXTURE],
        tmp_path,
    )
    panel_rows = pq.read_table(panel_path).to_pylist()

    assert panel_reference.canonical_dataset_name == "features.gfs_wave12_panel_non_sensitive"
    assert len(panel_reference.content_hash) == 64
    assert len(panel_rows) == 8
    assert all(row["sensitive_data_included"] is False for row in panel_rows)
    assert all(
        row["dataset_reference"].startswith("(features.gfs_wave12_panel_non_sensitive,")
        for row in panel_rows
    )

    outputs = build_gfs_wave12_marginals_country(panel_path, tmp_path)

    assert set(outputs) == {"JP", "US"}
    us_rows = pq.read_table(outputs["US"][0]).to_pylist()
    secure = next(row for row in us_rows if row["measure"] == "secure_flourish_index_12")
    flourish = next(row for row in us_rows if row["measure"] == "flourish_index_10")
    assert outputs["US"][1].canonical_dataset_name == "features.gfs_wave12_marginals_country_us"
    assert secure["weighted_mean"] == pytest.approx(6.95, abs=0.000001)
    assert flourish["weighted_mean"] == pytest.approx(7.2, abs=0.000001)


def test_gfs_request_status_stubs_do_not_contain_microdata() -> None:
    wave3 = build_gfs_request_status_stub(wave=3, request_scope="Wave 3 refresh")
    sensitive = build_gfs_request_status_stub(wave="sensitive", request_scope="Sensitive variables")

    assert wave3["access_status"] == "request_status_stub"
    assert sensitive["sensitive_data_access"] is False
    assert wave3["rows"] == []
    assert wave3["content_hash"] == wave3["dataset_reference"]["content_hash"]
    assert len(wave3["dataset_reference"]["content_hash"]) == 64


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
    assert "research-grade measurement" in card
    assert "prospective forecasting" in card


def test_advisor_review_queue_for_gfs_codebook_is_populated() -> None:
    queue = (ROOT / "docs" / "data" / "review" / "gfs-codebook-queue.md").read_text(
        encoding="utf-8"
    )

    assert "Confirm six-domain item wording" in queue
    assert "Confirm sampling weight interpretation" in queue
    assert "Pending" in queue
