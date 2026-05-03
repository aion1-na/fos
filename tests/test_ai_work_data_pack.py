from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.connectors.bls_oews import (
    parse_bls_employment_projections_fixture_only,
    parse_bls_laus_fixture_only,
    parse_bls_oews_fixture_only,
    parse_bls_qcew_fixture_only,
)
from fos_data_pipelines.connectors.cps import parse_cps_labor_context_fixture_only
from fos_data_pipelines.features.ai_exposure import (
    build_ai_exposure_ensemble,
    build_us_young_adult_ai_work_context,
)
from fos_data_pipelines.models import DatasetReferenceModel

ROOT = Path(__file__).resolve().parents[1]
AI_FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "ai_exposure"
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


def test_ai_work_context_joins_rs03_population_shape_and_emits_manifest(
    tmp_path: Path,
) -> None:
    agents_path = tmp_path / "rs03_agents.parquet"
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
            AI_FIXTURES / "eloundou_fixture_only.csv",
            AI_FIXTURES / "felten_fixture_only.csv",
            AI_FIXTURES / "acemoglu_restrepo_robot_exposure_fixture_only.csv",
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
        occupation_group_crosswalk_path=AI_FIXTURES / "occupation_group_crosswalk_fixture_only.csv",
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
                AI_FIXTURES / "occupation_group_crosswalk_fixture_only.csv",
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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert reference.canonical_dataset_name == "features.us_young_adult_ai_work_context"
    assert manifest["dataset_reference"] == {
        "canonical_dataset_name": reference.canonical_dataset_name,
        "version": reference.version,
        "content_hash": reference.content_hash,
    }
    assert manifest["source_inputs"]["occupation_ai_exposure_ensemble"] == str(ensemble_path)
    assert "dataset_references" in manifest
    assert len(manifest["dataset_references"]) == 9
    assert len(rows) == 3
    assert all(tuple(row["dataset_reference"]) == reference.as_tuple() for row in rows)
    assert all(row["occupation_crosswalk_version"] == "v0.1" for row in rows)
    assert all(row["ai_exposure_measure_count"] in {0, 3} for row in rows)
    assert [row for row in rows if row["labor_market_status"] == "not_in_labor_force"][0][
        "hourly_wage"
    ] is None


def test_ai_work_context_rejects_stale_source_references(tmp_path: Path) -> None:
    agents_path = tmp_path / "rs03_agents.parquet"
    pq.write_table(
        pa.Table.from_pylist(
            [{"agent_id": "ya-0", "occupation_group": "management_professional"}]
        ),
        agents_path,
    )
    ensemble_path, ensemble_reference = build_ai_exposure_ensemble(
        [AI_FIXTURES / "eloundou_fixture_only.csv", AI_FIXTURES / "felten_fixture_only.csv"],
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
    stale_population_reference = DatasetReferenceModel(
        canonical_dataset_name="features.us_young_adult_population",
        version="fixture-0.1",
        content_hash="0" * 64,
    )

    try:
        build_us_young_adult_ai_work_context(
            agents_path=agents_path,
            occupation_group_crosswalk_path=AI_FIXTURES / "occupation_group_crosswalk_fixture_only.csv",
            ensemble_path=ensemble_path,
            oews_path=Path(oews.stage_uri.removeprefix("file://")),
            laus_path=Path(laus.stage_uri.removeprefix("file://")),
            qcew_path=Path(qcew.stage_uri.removeprefix("file://")),
            employment_projections_path=Path(projections.stage_uri.removeprefix("file://")),
            cps_labor_context_path=Path(cps.stage_uri.removeprefix("file://")),
            output_dir=tmp_path / "context",
            source_dataset_references=[
                stale_population_reference,
                _reference(
                    "crosswalks.occupation_group_to_soc",
                    AI_FIXTURES / "occupation_group_crosswalk_fixture_only.csv",
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
    except ValueError as error:
        assert "do not match input content_hash values" in str(error)
    else:
        raise AssertionError("stale source dataset_reference was accepted")
