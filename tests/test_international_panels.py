from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.international_panels import (
    CROSS_COUNTRY_CONSTRUCTS,
    build_cross_country_employment_wellbeing_panels,
    build_safety_net_regime_comparators,
    load_international_panel_stubs,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "international_panels"


def test_panel_stubs_preserve_country_wave_weight_and_sampling_design() -> None:
    panels = load_international_panel_stubs(FIXTURES / "panel_stubs.json")
    assert {panel["country"] for panel in panels} == {"USA", "GBR", "DEU", "AUS", "EUR"}
    for panel in panels:
        assert panel["access_status"] == "request_status_stub"
        assert panel["license_status"] == "not_approved"
        assert panel["rows"] == []
        assert panel["wave_metadata"]["waves"] == ["request_status_stub"]
        assert panel["wave_metadata"]["weight_column"]
        assert panel["wave_metadata"]["sampling_design"]


def test_cross_country_feature_table_records_comparability_and_license_boundaries(
    tmp_path: Path,
) -> None:
    output_path, reference = build_cross_country_employment_wellbeing_panels(
        FIXTURES / "panel_stubs.json",
        FIXTURES / "canonical_codebook.json",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    assert reference.canonical_dataset_name == "features.cross_country_employment_wellbeing_panels"
    assert len(rows) == 5
    for row in rows:
        assert row["feature_table"] == "features.cross_country_employment_wellbeing_panels"
        assert set(row["constructs"]) == set(CROSS_COUNTRY_CONSTRUCTS)
        assert "approximate" in row["comparability"]
        assert row["weight_column"]
        assert row["sampling_design"]
        assert row["license_status"] == "not_approved"
        assert row["dataset_reference"].startswith(
            "(features.cross_country_employment_wellbeing_panels,"
        )


def test_safety_net_regime_comparators_include_required_countries(tmp_path: Path) -> None:
    output_path, reference = build_safety_net_regime_comparators(
        FIXTURES / "safety_net_regimes.json",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    assert reference.canonical_dataset_name == "features.safety_net_regime_comparators"
    assert {row["country"] for row in rows} == {"USA", "GBR", "DEU", "AUS", "EUR"}
    assert all(row["feature_table"] == "features.safety_net_regime_comparators" for row in rows)


def test_crosswalk_documents_comparable_and_approximate_constructs() -> None:
    crosswalk = (
        ROOT / "docs" / "data" / "crosswalks" / "cross-country-panels-v0.1.md"
    ).read_text(encoding="utf-8")
    for construct in ["Employment", "Education", "Income", "Family", "Health", "Well-being"]:
        assert construct in crosswalk
    assert "approximate" in crosswalk
    assert "comparable with caution" in crosswalk


def test_atlas_cross_country_comparison_view_lists_panel_family() -> None:
    page = (
        ROOT / "apps" / "atlas" / "app" / "international-panels" / "page.tsx"
    ).read_text(encoding="utf-8")
    source = (
        ROOT / "apps" / "atlas" / "lib" / "international" / "panels.ts"
    ).read_text(encoding="utf-8")
    assert "Cross-country longitudinal comparison" in page
    for label in ["PSID", "Understanding Society", "SOEP", "HILDA", "SHARE"]:
        assert label in source
    for country in ["USA", "GBR", "DEU", "AUS", "EUR"]:
        assert country in source
