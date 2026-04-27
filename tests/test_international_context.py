from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.international.context import (
    build_cross_country_dashboard_view,
    build_policy_regime_context,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "packages" / "data-pipelines" / "fixtures" / "international_context" / "policy_regime_fixture.csv"


def test_country_identifiers_map_to_iso3_and_preserve_source_codes(tmp_path: Path) -> None:
    output_path, reference = build_policy_regime_context(FIXTURE, tmp_path)
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.policy_regime_context"
    assert {row["source_country_code"] for row in rows} >= {"US", "USA", "JP", "JPN"}
    assert {row["country_iso3"] for row in rows} >= {"USA", "JPN", "DEU"}


def test_oecd_safety_net_queryable_with_flourishing_and_employment(tmp_path: Path) -> None:
    policy_path, _ = build_policy_regime_context(FIXTURE, tmp_path / "policy")
    dashboard_path = build_cross_country_dashboard_view(policy_path, tmp_path / "dashboard")
    rows = pq.read_table(dashboard_path).to_pylist()

    oecd_rows = [row for row in rows if row["source"] == "OECD"]
    assert {row["indicator"] for row in oecd_rows} == {"safety_net_generosity"}
    assert all(row["queryable_with"] == "flourishing_and_employment_indicators" for row in rows)
    assert all(row["view_name"] == "atlas.cross_country_policy_dashboard" for row in rows)


def test_international_data_card_documents_public_table_microdata_limitations() -> None:
    card = (
        ROOT / "docs" / "data" / "datasets" / "international-policy-context.md"
    ).read_text(encoding="utf-8")
    assert "public table" in card.lower()
    assert "microdata" in card.lower()
    assert "ISO3" in card


def test_atlas_international_view_has_materialized_dashboard_rows() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "international" / "page.tsx").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "apps" / "atlas" / "lib" / "international" / "context.ts").read_text(
        encoding="utf-8"
    )
    assert "atlas.cross_country_policy_dashboard" in source
    assert "safety_net_generosity" in source
    assert "employment_rate" in source
    assert "ISO3" in page
