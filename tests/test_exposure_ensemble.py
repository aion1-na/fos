from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.features.ai_exposure import (
    build_ai_exposure_ensemble,
    build_occupation_ai_demographic_distributions,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "ai_exposure"


def test_headline_exposure_ensemble_uses_multiple_scores(tmp_path: Path) -> None:
    output_path, reference = build_ai_exposure_ensemble(
        [
            FIXTURES / "eloundou_fixture_only.csv",
            FIXTURES / "felten_fixture_only.csv",
            FIXTURES / "acemoglu_restrepo_robot_exposure_fixture_only.csv",
        ],
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.occupation_ai_exposure_ensemble"
    assert all(row["measure_count"] >= 2 for row in rows)
    assert all(row["single_score_headline_allowed"] is False for row in rows)
    assert all(tuple(row["dataset_reference"]) == reference.as_tuple() for row in rows)


def test_sparse_single_measure_occupations_are_excluded_from_headlines(tmp_path: Path) -> None:
    sparse = tmp_path / "sparse_fixture_only.csv"
    sparse.write_text(
        "\n".join(
            [
                "occupation_code,exposure_score,measure_name,measure_version",
                "99-9999,0.40,sparse_source,fixture-0.1",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_path, _ = build_ai_exposure_ensemble(
        [FIXTURES / "eloundou_fixture_only.csv", FIXTURES / "felten_fixture_only.csv", sparse],
        tmp_path / "ensemble",
    )
    rows = pq.read_table(output_path).to_pylist()

    assert "99-9999" not in {row["occupation_code"] for row in rows}


def test_exposure_disagreement_is_reported_by_demographic_subgroup(
    tmp_path: Path,
) -> None:
    ensemble_path, _ = build_ai_exposure_ensemble(
        [FIXTURES / "eloundou_fixture_only.csv", FIXTURES / "felten_fixture_only.csv"],
        tmp_path / "ensemble",
    )
    output_path, reference = build_occupation_ai_demographic_distributions(
        ensemble_path,
        FIXTURES / "demographics_fixture_only.csv",
        tmp_path / "distributions",
    )
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.occupation_ai_demographic_distributions"
    assert rows
    assert all(tuple(row["dataset_reference"]) == reference.as_tuple() for row in rows)
    assert all("range_disagreement" in row for row in rows)
    assert all(row["uncertainty_signal"] == "exposure_measure_disagreement_by_subgroup" for row in rows)
