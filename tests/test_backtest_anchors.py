from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.backtests.replication import (
    build_adh_china_shock_panel,
    build_pntr_mortality_backtest,
    build_robot_exposure_table,
    load_replication_archive,
    validate_china_shock_gate,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "backtests"
ADH = FIXTURES / "adh_china_shock"


def test_replication_archive_lands_immutably_with_checksums_and_citation() -> None:
    first = load_replication_archive(ADH)
    second = load_replication_archive(ADH)

    assert first.content_hash == second.content_hash
    assert len(first.content_hash) == 64
    assert "Autor, Dorn, and Hanson" in first.source_citation
    assert set(first.file_hashes) == {
        "china_shock_fixture.dta.json",
        "build_panel_fixture.do",
    }


def test_stata_parsing_preserves_labels_and_source_variable_names() -> None:
    archive = load_replication_archive(ADH)

    assert archive.variable_labels["d_tradeusch_pw"] == "Import exposure per worker"
    assert archive.variable_labels["manufacturing_share"] == "Manufacturing employment share"
    assert archive.source_variable_names == (
        "czone",
        "year",
        "d_tradeusch_pw",
        "manufacturing_share",
    )


def test_backtest_feature_tables_carry_raw_archive_provenance(tmp_path: Path) -> None:
    panel_path, panel_ref = build_adh_china_shock_panel(ADH, tmp_path / "adh")
    archive = load_replication_archive(ADH)
    pntr_path, pntr_ref = build_pntr_mortality_backtest(
        FIXTURES / "pntr_mortality" / "pntr_mortality_fixture.csv",
        tmp_path / "pntr",
        archive.content_hash,
    )
    robot_path, robot_ref = build_robot_exposure_table(
        FIXTURES / "robot_exposure" / "robot_exposure_fixture.csv",
        tmp_path / "robot",
        archive.content_hash,
    )

    for path in [panel_path, pntr_path, robot_path]:
        rows = pq.read_table(path).to_pylist()
        assert rows
        assert all(row["raw_archive_hash"] == archive.content_hash for row in rows)

    assert panel_ref.canonical_dataset_name == "features.adh_china_shock_panel"
    assert pntr_ref.canonical_dataset_name == "features.pntr_mortality_backtest"
    assert robot_ref.canonical_dataset_name == "features.robot_exposure"


def test_validation_harness_fails_closed_when_references_are_missing() -> None:
    passed, missing = validate_china_shock_gate(
        {
            "features.adh_china_shock_panel": "s3://fixture/panel.parquet",
            "raw_archive_hash": None,
            "connector_version": "0.1.0",
            "source_citation": "Autor, Dorn, and Hanson",
            "stata_variable_label_manifest": "labels.json",
        }
    )

    assert passed is False
    assert missing == ["raw_archive_hash"]


def test_validation_harness_passes_when_all_references_exist() -> None:
    passed, missing = validate_china_shock_gate(
        {
            "features.adh_china_shock_panel": "s3://fixture/panel.parquet",
            "raw_archive_hash": "a" * 64,
            "connector_version": "0.1.0",
            "source_citation": "Autor, Dorn, and Hanson",
            "stata_variable_label_manifest": "labels.json",
        }
    )

    assert passed is True
    assert missing == []


def test_atlas_backtest_viewer_has_geography_and_demographic_slices() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "backtests" / "page.tsx").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "apps" / "atlas" / "lib" / "backtests" / "anchors.ts").read_text(
        encoding="utf-8"
    )

    assert "Geography and demographic slices" in page
    assert "validationGate" in page
    assert "demographicGroup" in source
    assert "robotExposure" in source
