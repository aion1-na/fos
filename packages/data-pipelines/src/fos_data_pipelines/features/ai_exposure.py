from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from statistics import mean, pstdev

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel


@dataclass(frozen=True, slots=True)
class ExposureMeasure:
    occupation_code: str
    measure_name: str
    measure_version: str
    exposure_score: float


def load_exposure_csv(path: Path) -> list[ExposureMeasure]:
    rows = csv.DictReader(path.read_text(encoding="utf-8").splitlines())
    return [
        ExposureMeasure(
            occupation_code=row["occupation_code"],
            measure_name=row["measure_name"],
            measure_version=row["measure_version"],
            exposure_score=float(row["exposure_score"]),
        )
        for row in rows
    ]


def _combined_hash(paths: list[Path]) -> str:
    digest = sha256()
    for path in sorted(paths, key=lambda item: str(item)):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _disagreement_level(value: float) -> str:
    if value >= 0.20:
        return "high"
    if value >= 0.08:
        return "medium"
    return "low"


def build_ai_exposure_ensemble(
    exposure_paths: list[Path],
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    measures: dict[str, list[ExposureMeasure]] = defaultdict(list)
    for path in exposure_paths:
        for measure in load_exposure_csv(path):
            measures[measure.occupation_code].append(measure)

    rows: list[dict[str, object]] = []
    for occupation_code, occupation_measures in sorted(measures.items()):
        if len(occupation_measures) < 2:
            raise ValueError("headline AI exposure ensemble requires at least two measures")
        scores = [item.exposure_score for item in occupation_measures]
        measure_names = sorted(item.measure_name for item in occupation_measures)
        disagreement = max(scores) - min(scores)
        rows.append(
            {
                "occupation_code": occupation_code,
                "measure_names": ",".join(measure_names),
                "measure_count": len(scores),
                "mean_exposure": mean(scores),
                "min_exposure": min(scores),
                "max_exposure": max(scores),
                "range_disagreement": disagreement,
                "standard_deviation": pstdev(scores),
                "disagreement_level": _disagreement_level(disagreement),
                "uncertainty_signal": "exposure_measure_disagreement",
                "single_score_headline_allowed": False,
            }
        )

    content_hash = _combined_hash(exposure_paths)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.ai_exposure_ensemble-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.ai_exposure_ensemble",
        version=dataset_version,
        content_hash=content_hash,
    )


def _read_parquet(path: Path) -> list[dict[str, object]]:
    return pq.read_table(path).to_pylist()


def _index_by(rows: list[dict[str, object]], key: str) -> dict[str, dict[str, object]]:
    return {str(row[key]): row for row in rows}


def _content_hash_for_payload(payload: object) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


def build_us_young_adult_ai_work_context(
    *,
    agents_path: Path,
    occupation_group_crosswalk_path: Path,
    ensemble_path: Path,
    oews_path: Path,
    laus_path: Path,
    qcew_path: Path,
    employment_projections_path: Path,
    cps_labor_context_path: Path,
    output_dir: Path,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, Path, DatasetReferenceModel]:
    group_to_soc = {
        row["occupation_group"]: row["occupation_code"]
        for row in csv.DictReader(
            occupation_group_crosswalk_path.read_text(encoding="utf-8").splitlines()
        )
    }
    ensemble = _index_by(_read_parquet(ensemble_path), "occupation_code")
    oews = _index_by(_read_parquet(oews_path), "occupation_code")
    projections = _index_by(_read_parquet(employment_projections_path), "occupation_code")
    cps = _index_by(_read_parquet(cps_labor_context_path), "occupation_group")
    laus_us = next(
        row for row in _read_parquet(laus_path) if str(row["area_code"]).startswith("US")
    )
    qcew_us = next(row for row in _read_parquet(qcew_path) if str(row["area_fips"]) == "US")

    rows: list[dict[str, object]] = []
    for agent in _read_parquet(agents_path):
        occupation_group = str(agent.get("occupation_group", "not_in_labor_force"))
        occupation_code = group_to_soc[occupation_group]
        exposure = ensemble[occupation_code]
        wage = oews[occupation_code]
        projection = projections[occupation_code]
        context = cps.get(occupation_group, {})
        rows.append(
            {
                "agent_id": agent["agent_id"],
                "age_band": agent.get("age_band"),
                "education": agent.get("education"),
                "geography": agent.get("geography"),
                "occupation_group": occupation_group,
                "occupation_code": occupation_code,
                "ai_exposure_mean": float(exposure["mean_exposure"]),
                "ai_exposure_measure_count": int(exposure["measure_count"]),
                "ai_exposure_range_disagreement": float(exposure["range_disagreement"]),
                "ai_exposure_disagreement_level": exposure["disagreement_level"],
                "single_score_headline_allowed": bool(
                    exposure["single_score_headline_allowed"]
                ),
                "hourly_wage": float(wage["hourly_wage"]),
                "unemployment_rate": float(laus_us["unemployment_rate"]),
                "labor_force": int(laus_us["labor_force"]),
                "annual_average_employment": int(qcew_us["annual_average_employment"]),
                "projected_growth_pct": float(projection["projected_growth_pct"]),
                "typical_entry_education": projection["typical_entry_education"],
                "young_adult_share": float(context.get("young_adult_share", 0.0)),
            }
        )

    content_hash = _content_hash_for_payload(
        {
            "agents": sha256(agents_path.read_bytes()).hexdigest(),
            "crosswalk": sha256(occupation_group_crosswalk_path.read_bytes()).hexdigest(),
            "ensemble": sha256(ensemble_path.read_bytes()).hexdigest(),
            "oews": sha256(oews_path.read_bytes()).hexdigest(),
            "laus": sha256(laus_path.read_bytes()).hexdigest(),
            "qcew": sha256(qcew_path.read_bytes()).hexdigest(),
            "employment_projections": sha256(employment_projections_path.read_bytes()).hexdigest(),
            "cps_labor_context": sha256(cps_labor_context_path.read_bytes()).hexdigest(),
        }
    )
    reference = DatasetReferenceModel(
        canonical_dataset_name="features.us_young_adult_ai_work_context",
        version=dataset_version,
        content_hash=content_hash,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.us_young_adult_ai_work_context-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)

    manifest = {
        "feature_table": "features.us_young_adult_ai_work_context",
        "dataset_reference": {
            "canonical_dataset_name": reference.canonical_dataset_name,
            "version": reference.version,
            "content_hash": reference.content_hash,
        },
        "source_inputs": {
            "agents": str(agents_path),
            "occupation_group_crosswalk": str(occupation_group_crosswalk_path),
            "ai_exposure_ensemble": str(ensemble_path),
            "bls_oews": str(oews_path),
            "bls_laus": str(laus_path),
            "bls_qcew": str(qcew_path),
            "bls_employment_projections": str(employment_projections_path),
            "cps_labor_context": str(cps_labor_context_path),
        },
        "quality_profile": {
            "row_count": len(rows),
            "minimum_exposure_measures_per_row": min(
                row["ai_exposure_measure_count"] for row in rows
            )
            if rows
            else 0,
            "single_score_headlines_allowed": False,
        },
    }
    manifest_path = output_dir / f"features.us_young_adult_ai_work_context-{content_hash}.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path, manifest_path, reference


def _quartile(value: float) -> int:
    if value >= 0.75:
        return 4
    if value >= 0.50:
        return 3
    if value >= 0.25:
        return 2
    return 1


def build_occupation_ai_demographic_distributions(
    ensemble_path: Path,
    demographics_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    ensemble = {
        row["occupation_code"]: row
        for row in pq.read_table(ensemble_path).to_pylist()
    }
    demographic_rows = csv.DictReader(demographics_path.read_text(encoding="utf-8").splitlines())
    rows: list[dict[str, object]] = []
    for row in demographic_rows:
        exposure = ensemble[row["occupation_code"]]
        rows.append(
            {
                "occupation_code": row["occupation_code"],
                "demographic_group": row["demographic_group"],
                "geography": row["geography"],
                "worker_count": int(row["worker_count"]),
                "exposure_quartile": _quartile(float(exposure["mean_exposure"])),
                "range_disagreement": exposure["range_disagreement"],
                "disagreement_level": exposure["disagreement_level"],
            }
        )

    content_hash = _combined_hash([ensemble_path, demographics_path])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (
        f"features.occupation_ai_demographic_distributions-{content_hash}.parquet"
    )
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.occupation_ai_demographic_distributions",
        version=dataset_version,
        content_hash=content_hash,
    )
