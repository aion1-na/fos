from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.us_panels import US_PANEL_CONSTRUCTS, build_us_employment_wellbeing_panels

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "us_panels"


def test_us_employment_wellbeing_feature_table_is_training_ready(tmp_path: Path) -> None:
    stub_paths = sorted(FIXTURES.glob("*_registration_stub.json"))
    output_path, reference = build_us_employment_wellbeing_panels(
        FIXTURES / "harmonized_codebook.json",
        FIXTURES / "wave_metadata.json",
        FIXTURES / "quality_profiles.json",
        stub_paths,
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    assert reference.canonical_dataset_name == "features.us_employment_wellbeing_panels"
    assert len(rows) == 5
    for row in rows:
        assert row["feature_table"] == "features.us_employment_wellbeing_panels"
        assert row["access_status"] == "request_status_stub"
        assert row["license_status"] == "not_approved"
        assert row["registration_required"] is True
        assert set(row["constructs"]) == set(US_PANEL_CONSTRUCTS)
        assert row["usable_by_training"] is True
        assert row["dataset_reference"].startswith("(features.us_employment_wellbeing_panels,")


def test_dua_restrictions_are_visible_in_feature_rows(tmp_path: Path) -> None:
    output_path, _reference = build_us_employment_wellbeing_panels(
        FIXTURES / "harmonized_codebook.json",
        FIXTURES / "wave_metadata.json",
        FIXTURES / "quality_profiles.json",
        sorted(FIXTURES.glob("*_registration_stub.json")),
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    assert all(row["license_status"] == "not_approved" for row in rows)
    assert all("pending_access" in row["quality_profile"] for row in rows)
