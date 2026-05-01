from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.community import build_place_context

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "community_context"


def test_place_context_uses_only_supported_public_aggregate_joins(tmp_path: Path) -> None:
    output_path, reference = build_place_context(
        FIXTURES / "place_context_fixture_only.csv",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.place_context"
    assert rows
    assert {row["geography_level"] for row in rows} == {"county", "country"}
    assert "private_archive" not in {row["source_geography_id"] for row in rows}
    assert {row["join_key"] for row in rows} == {"county_fips", "country_iso3"}
    assert all(row["causal_interpretation"] == "not_causal_proof" for row in rows)
    assert {row["suppressed"] for row in rows} == {False}


def test_place_context_rejects_invalid_existing_join_keys(tmp_path: Path) -> None:
    fixture = tmp_path / "bad_place_fixture_only.csv"
    fixture.write_text(
        "\n".join(
            [
                "source,construct,source_geography_id,geography_level,join_allowed,year,measure,value,source_label,join_key,join_segment,pathway_role,cell_count",
                "OpportunityAtlas,place_opportunity,06075,county,true,2021,upward_mobility_index,0.58,San Francisco County,restricted_person_id,all,calibration,120",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_path, _ = build_place_context(fixture, tmp_path / "out")
    rows = pq.read_table(output_path).to_pylist()

    assert rows == []
