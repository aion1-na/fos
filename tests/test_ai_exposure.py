from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.connectors.ai_exposure import (
    parse_anthropic_economic_index_request_status_stub,
    parse_eloundou_fixture,
    parse_felten_fixture,
    parse_webb_request_status_stub,
)
from fos_data_pipelines.crosswalks.occupations import load_crosswalk
from fos_data_pipelines.features.ai_exposure import (
    build_ai_exposure_ensemble,
    build_occupation_ai_demographic_distributions,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "ai_exposure"
CODEBOOK = ROOT / "codebooks" / "ai_exposure_measures.yaml"


def test_eloundou_and_felten_can_be_queried_side_by_side(tmp_path: Path) -> None:
    eloundou = parse_eloundou_fixture(FIXTURES / "eloundou_fixture.csv", CODEBOOK, tmp_path / "staged")
    felten = parse_felten_fixture(FIXTURES / "felten_fixture.csv", CODEBOOK, tmp_path / "staged")

    eloundou_rows = pq.read_table(Path(eloundou.stage_uri.removeprefix("file://"))).to_pylist()
    felten_rows = pq.read_table(Path(felten.stage_uri.removeprefix("file://"))).to_pylist()

    side_by_side = {
        row["occupation_code"]: {"eloundou": row["exposure_score"]}
        for row in eloundou_rows
    }
    for row in felten_rows:
        side_by_side[row["occupation_code"]]["felten"] = row["exposure_score"]

    assert side_by_side["15-1252"] == {"eloundou": "0.82", "felten": "0.77"}
    assert all(set(values) == {"eloundou", "felten"} for values in side_by_side.values())


def test_request_status_connectors_do_not_fetch_unapproved_data() -> None:
    webb = parse_webb_request_status_stub(FIXTURES / "webb_request_status_stub.json")
    anthropic = parse_anthropic_economic_index_request_status_stub(
        FIXTURES / "anthropic_economic_index_request_status_stub.json"
    )

    assert webb["access_status"] == "request_status_stub"
    assert anthropic["access_status"] == "request_status_stub"
    assert webb["rows"] == []
    assert anthropic["rows"] == []


def test_ai_exposure_ensemble_requires_multiple_measures_and_records_uncertainty(
    tmp_path: Path,
) -> None:
    ensemble_path, reference = build_ai_exposure_ensemble(
        [FIXTURES / "eloundou_fixture.csv", FIXTURES / "felten_fixture.csv"],
        tmp_path,
    )
    table = pq.read_table(ensemble_path)
    rows = {row["occupation_code"]: row for row in table.to_pylist()}

    assert reference.canonical_dataset_name == "features.ai_exposure_ensemble"
    assert rows["15-1252"]["measure_count"] == 2
    assert rows["15-1252"]["single_score_headline_allowed"] is False
    assert rows["15-1252"]["uncertainty_signal"] == "exposure_measure_disagreement"
    assert round(rows["15-1252"]["range_disagreement"], 2) == 0.05


def test_single_measure_headline_output_is_rejected(tmp_path: Path) -> None:
    try:
        build_ai_exposure_ensemble([FIXTURES / "eloundou_fixture.csv"], tmp_path)
    except ValueError as error:
        assert "requires at least two measures" in str(error)
    else:
        raise AssertionError("single-measure headline output was allowed")


def test_crosswalk_is_versioned_and_reversible_where_possible() -> None:
    crosswalk = load_crosswalk(FIXTURES / "soc_onet_census_crosswalk_v0.1.csv", version="0.1")

    assert crosswalk.version == "0.1"
    assert crosswalk.soc_to_onet("15-1252") == "15-1252.00"
    assert crosswalk.onet_to_soc("15-1252.00") == "15-1252"
    assert crosswalk.census_to_canonical("1020") == "15-1252"


def test_occupation_ai_demographic_distributions_include_quartiles(tmp_path: Path) -> None:
    ensemble_path, _ = build_ai_exposure_ensemble(
        [FIXTURES / "eloundou_fixture.csv", FIXTURES / "felten_fixture.csv"],
        tmp_path / "ensemble",
    )
    distributions_path, reference = build_occupation_ai_demographic_distributions(
        ensemble_path,
        FIXTURES / "demographics_fixture.csv",
        tmp_path / "distributions",
    )
    rows = pq.read_table(distributions_path).to_pylist()

    assert reference.canonical_dataset_name == "features.occupation_ai_demographic_distributions"
    assert rows
    assert {row["geography"] for row in rows} == {"US"}
    assert {row["exposure_quartile"] for row in rows} >= {2, 3, 4}
