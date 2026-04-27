from __future__ import annotations

import csv
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
