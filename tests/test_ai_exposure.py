from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.connectors.ai_exposure import (
    parse_acemoglu_restrepo_robot_fixture_only,
    parse_anthropic_economic_index_request_status_stub,
    parse_eloundou_fixture,
    parse_felten_fixture,
    parse_webb_request_status_stub,
)
from fos_data_pipelines.connectors.bls_oews import (
    parse_bls_employment_projections_fixture_only,
    parse_bls_laus_fixture_only,
    parse_bls_oews_fixture_only,
    parse_bls_qcew_fixture_only,
)
from fos_data_pipelines.connectors.cps import parse_cps_labor_context_fixture_only
from fos_data_pipelines.crosswalks.occupations import load_crosswalk
from fos_data_pipelines.features.ai_exposure import (
    build_ai_exposure_ensemble,
    build_occupation_ai_demographic_distributions,
    build_us_young_adult_ai_work_context,
)
from fos_data_pipelines.models import DatasetReferenceModel

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "ai_exposure"
CODEBOOK = ROOT / "codebooks" / "ai_exposure_measures.yaml"
BLS_FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "bls"
CPS_FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "cps"
CODEBOOKS = ROOT / "codebooks"


def _reference(canonical_dataset_name: str, path: Path, version: str = "fixture-0.1") -> DatasetReferenceModel:
    return DatasetReferenceModel(
        canonical_dataset_name=canonical_dataset_name,
        version=version,
        content_hash=sha256(path.read_bytes()).hexdigest(),
    )


def _staged_reference(
    canonical_dataset_name: str, path: Path, version: str = "fixture-0.1"
) -> DatasetReferenceModel:
    return DatasetReferenceModel(
        canonical_dataset_name=canonical_dataset_name,
        version=version,
        content_hash=path.stem.rsplit("-", 1)[-1],
    )


def test_eloundou_and_felten_can_be_queried_side_by_side(tmp_path: Path) -> None:
    eloundou = parse_eloundou_fixture(
        FIXTURES / "eloundou_fixture_only.csv", CODEBOOK, tmp_path / "staged"
    )
    felten = parse_felten_fixture(
        FIXTURES / "felten_fixture_only.csv", CODEBOOK, tmp_path / "staged"
    )

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
    assert eloundou.transform_ref.startswith("eloundou_fixture_only@")
    assert felten.transform_ref.startswith("felten_fixture_only@")


def test_robot_exposure_archive_ingester_preserves_source_occupation_codes(
    tmp_path: Path,
) -> None:
    robot = parse_acemoglu_restrepo_robot_fixture_only(
        FIXTURES / "acemoglu_restrepo_robot_exposure_fixture_only.csv",
        ROOT / "codebooks" / "acemoglu_restrepo_robot_exposure.yaml",
        tmp_path / "robot",
    )
    rows = pq.read_table(Path(robot.stage_uri.removeprefix("file://"))).to_pylist()

    assert robot.transform_ref == "acemoglu_restrepo_robot_fixture_only@0.1.0"
    assert {row["occupation_code"] for row in rows} == {"15-1252", "29-1141", "43-4051"}


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
        [
            FIXTURES / "eloundou_fixture_only.csv",
            FIXTURES / "felten_fixture_only.csv",
            FIXTURES / "acemoglu_restrepo_robot_exposure_fixture_only.csv",
        ],
        tmp_path,
    )
    table = pq.read_table(ensemble_path)
    rows = {row["occupation_code"]: row for row in table.to_pylist()}

    assert reference.canonical_dataset_name == "features.occupation_ai_exposure_ensemble"
    assert rows["15-1252"]["measure_count"] == 3
    assert rows["15-1252"]["single_score_headline_allowed"] is False
    assert rows["15-1252"]["uncertainty_signal"] == "exposure_measure_disagreement"
    assert tuple(rows["15-1252"]["dataset_reference"]) == reference.as_tuple()
    assert round(rows["15-1252"]["range_disagreement"], 2) == 0.47


def test_single_measure_headline_output_is_rejected(tmp_path: Path) -> None:
    try:
        build_ai_exposure_ensemble([FIXTURES / "eloundou_fixture_only.csv"], tmp_path)
    except ValueError as error:
        assert "requires at least two distinct measures" in str(error)
    else:
        raise AssertionError("single-measure headline output was allowed")


def test_duplicate_measure_headline_output_is_rejected(tmp_path: Path) -> None:
    try:
        build_ai_exposure_ensemble(
            [FIXTURES / "eloundou_fixture_only.csv", FIXTURES / "eloundou_fixture_only.csv"],
            tmp_path,
        )
    except ValueError as error:
        assert "cannot duplicate a measure" in str(error)
    else:
        raise AssertionError("duplicate-measure headline output was allowed")


def test_crosswalk_is_versioned_and_reversible_where_possible() -> None:
    crosswalk = load_crosswalk(FIXTURES / "soc_onet_census_crosswalk_v0.1.csv", version="0.1")

    assert crosswalk.version == "0.1"
    assert crosswalk.soc_to_onet("15-1252") == "15-1252.00"
    assert crosswalk.onet_to_soc("15-1252.00") == "15-1252"
    assert crosswalk.census_to_canonical("1020") == "15-1252"
    assert {
        (row["soc_code"], row["onet_soc_code"], row["census_occ_code"], row["source_label"])
        for row in crosswalk.source_codes()
    } >= {("15-1252", "15-1252.00", "1020", "software developers")}


def test_occupation_ai_demographic_distributions_include_quartiles(tmp_path: Path) -> None:
    ensemble_path, ensemble_reference = build_ai_exposure_ensemble(
        [FIXTURES / "eloundou_fixture_only.csv", FIXTURES / "felten_fixture_only.csv"],
        tmp_path / "ensemble",
    )
    distributions_path, reference = build_occupation_ai_demographic_distributions(
        ensemble_path,
        FIXTURES / "demographics_fixture_only.csv",
        tmp_path / "distributions",
    )
    rows = pq.read_table(distributions_path).to_pylist()

    assert reference.canonical_dataset_name == "features.occupation_ai_demographic_distributions"
    assert rows
    assert {row["geography"] for row in rows} == {"US"}
    assert {row["exposure_quartile"] for row in rows} >= {2, 3, 4}
    assert all(row["measure_count"] == 2 for row in rows)
    assert all(row["uncertainty_signal"] == "exposure_measure_disagreement_by_subgroup" for row in rows)
    assert all(row["single_score_headline_allowed"] is False for row in rows)


def test_us_young_adult_ai_work_context_joins_population_to_labor_and_ensemble(
    tmp_path: Path,
) -> None:
    agents_path = tmp_path / "agents.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [
                {
                    "agent_id": "ya-0",
                    "age_band": "21-24",
                    "education": "bachelor_plus",
                    "geography": "midwest",
                    "occupation_group": "management_professional",
                },
                {
                    "agent_id": "ya-1",
                    "age_band": "25-29",
                    "education": "high_school",
                    "geography": "south",
                    "occupation_group": "service",
                },
                {
                    "agent_id": "ya-2",
                    "age_band": "18-20",
                    "education": "some_college",
                    "geography": "west",
                    "occupation_group": "not_in_labor_force",
                },
            ]
        ),
        agents_path,
    )
    ensemble_path, ensemble_reference = build_ai_exposure_ensemble(
        [
            FIXTURES / "eloundou_fixture_only.csv",
            FIXTURES / "felten_fixture_only.csv",
            FIXTURES / "acemoglu_restrepo_robot_exposure_fixture_only.csv",
        ],
        tmp_path / "ensemble",
    )
    oews = parse_bls_oews_fixture_only(
        BLS_FIXTURES / "oews_fixture_only.json",
        CODEBOOKS / "bls_oews.yaml",
        tmp_path / "oews",
    )
    laus = parse_bls_laus_fixture_only(
        BLS_FIXTURES / "laus_fixture_only.csv",
        CODEBOOKS / "bls_laus.yaml",
        tmp_path / "laus",
    )
    qcew = parse_bls_qcew_fixture_only(
        BLS_FIXTURES / "qcew_fixture_only.csv",
        CODEBOOKS / "bls_qcew.yaml",
        tmp_path / "qcew",
    )
    projections = parse_bls_employment_projections_fixture_only(
        BLS_FIXTURES / "employment_projections_fixture_only.csv",
        CODEBOOKS / "bls_employment_projections.yaml",
        tmp_path / "ep",
    )
    cps = parse_cps_labor_context_fixture_only(
        CPS_FIXTURES / "labor_context_fixture_only.csv",
        CODEBOOKS / "cps_labor_context.yaml",
        tmp_path / "cps",
    )

    output_path, manifest_path, reference = build_us_young_adult_ai_work_context(
        agents_path=agents_path,
        occupation_group_crosswalk_path=FIXTURES / "occupation_group_crosswalk_fixture_only.csv",
        ensemble_path=ensemble_path,
        oews_path=Path(oews.stage_uri.removeprefix("file://")),
        laus_path=Path(laus.stage_uri.removeprefix("file://")),
        qcew_path=Path(qcew.stage_uri.removeprefix("file://")),
        employment_projections_path=Path(projections.stage_uri.removeprefix("file://")),
        cps_labor_context_path=Path(cps.stage_uri.removeprefix("file://")),
        output_dir=tmp_path / "context",
        source_dataset_references=[
            _reference("features.us_young_adult_population", agents_path),
            _reference(
                "crosswalks.occupation_group_to_soc",
                FIXTURES / "occupation_group_crosswalk_fixture_only.csv",
                "v0.1",
            ),
            ensemble_reference,
            _staged_reference("bls_oews", Path(oews.stage_uri.removeprefix("file://"))),
            _staged_reference("bls_laus", Path(laus.stage_uri.removeprefix("file://"))),
            _staged_reference("bls_qcew", Path(qcew.stage_uri.removeprefix("file://"))),
            _staged_reference(
                "bls_employment_projections",
                Path(projections.stage_uri.removeprefix("file://")),
            ),
            _staged_reference("cps_labor_context", Path(cps.stage_uri.removeprefix("file://"))),
        ],
    )
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.us_young_adult_ai_work_context"
    assert manifest_path.exists()
    assert len(rows) == 3
    assert {row["occupation_code"] for row in rows} == {"15-1252", "29-1141", None}
    assert [row for row in rows if row["occupation_code"] is None][0]["hourly_wage"] is None
    assert [row for row in rows if row["occupation_code"] is None][0]["ai_exposure_mean"] is None
    assert all(row["occupation_crosswalk_version"] == "v0.1" for row in rows)
    assert all(row["ai_exposure_measure_count"] in {0, 3} for row in rows)
    assert all(row["single_score_headline_allowed"] is False for row in rows)
    assert all(tuple(row["dataset_reference"]) == reference.as_tuple() for row in rows)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "dataset_references" in manifest
    assert manifest["quality_profile"]["not_in_labor_force_rows_have_exposure"] is False
