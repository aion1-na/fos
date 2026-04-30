from __future__ import annotations

import csv
import json
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Iterable

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.connectors.gfs import assert_gfs_non_sensitive_rows
from fos_data_pipelines.models import DatasetReferenceModel

DOMAIN_FIELDS = ("happiness", "health", "meaning", "character", "relationships", "financial")
ITEM_DOMAINS = {
    "happiness": ("happiness_1", "happiness_2"),
    "health": ("health_1", "health_2"),
    "meaning": ("meaning_1", "meaning_2"),
    "character": ("character_1", "character_2"),
    "relationships": ("relationships_1", "relationships_2"),
    "financial": ("financial_1", "financial_2"),
}
FLOURISH_INDEX_ITEMS = tuple(
    item for domain in DOMAIN_FIELDS if domain != "financial" for item in ITEM_DOMAINS[domain]
)
SECURE_FLOURISH_INDEX_ITEMS = tuple(item for domain in DOMAIN_FIELDS for item in ITEM_DOMAINS[domain])


def _weighted_mean(values: list[tuple[float, float]]) -> float:
    numerator = sum(value * weight for value, weight in values)
    denominator = sum(weight for _, weight in values)
    if denominator == 0:
        raise ValueError("sampling weights must sum to a positive value")
    return numerator / denominator


def _read_rows(path: Path) -> list[dict[str, str]]:
    rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    assert_gfs_non_sensitive_rows(rows)
    return rows


def _row_mean(row: dict[str, object], fields: Iterable[str]) -> float:
    values = [float(row[field]) for field in fields if str(row.get(field, "")) != ""]
    if not values:
        raise ValueError(f"row is missing all required fields: {tuple(fields)}")
    return sum(values) / len(values)


def score_flourishing_row(row: dict[str, object]) -> dict[str, float]:
    """Score 10-item Flourish and 12-item Secure Flourish indices from item-level GFS rows."""

    domain_scores = {
        domain: _row_mean(row, items) if all(item in row for item in items) else float(row[domain])
        for domain, items in ITEM_DOMAINS.items()
    }
    item_scores = {
        "flourish_index_10": _row_mean(row, FLOURISH_INDEX_ITEMS)
        if all(item in row for item in FLOURISH_INDEX_ITEMS)
        else sum(domain_scores[domain] for domain in DOMAIN_FIELDS if domain != "financial") / 5,
        "secure_flourish_index_12": _row_mean(row, SECURE_FLOURISH_INDEX_ITEMS)
        if all(item in row for item in SECURE_FLOURISH_INDEX_ITEMS)
        else sum(domain_scores.values()) / 6,
    }
    return {**domain_scores, **item_scores}


def score_gfs_rows(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    scored = []
    for row in rows:
        scored.append({**row, **score_flourishing_row(row)})
    return scored


def score_six_domain_country_marginals(fixture_path: Path) -> dict[str, dict[str, float]]:
    rows = score_gfs_rows(_read_rows(fixture_path))
    grouped: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(
        lambda: {domain: [] for domain in DOMAIN_FIELDS}
    )
    for row in rows:
        country = row["country"]
        weight = float(row["weight"])
        for domain in DOMAIN_FIELDS:
            grouped[country][domain].append((float(row[domain]), weight))

    return {
        country: {
            domain: round(_weighted_mean(values), 6)
            for domain, values in domains.items()
        }
        for country, domains in sorted(grouped.items())
    }


def build_gfs_wave1_marginals(
    fixture_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> dict[str, tuple[Path, DatasetReferenceModel]]:
    marginals = score_six_domain_country_marginals(fixture_path)
    content_hash = sha256(fixture_path.read_bytes()).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, tuple[Path, DatasetReferenceModel]] = {}
    for country, values in marginals.items():
        canonical_name = f"features.gfs_wave1_marginals_country_{country.lower()}"
        rows = [
            {
                "country": country,
                "domain": domain,
                "weighted_mean": value,
                "sampling_weighted": True,
                "measurement_mode": "cross_sectional_research_grade",
            }
            for domain, value in values.items()
        ]
        path = output_dir / f"{canonical_name}-{content_hash}.parquet"
        pq.write_table(pa.Table.from_pylist(rows), path)
        outputs[country] = (
            path,
            DatasetReferenceModel(
                canonical_dataset_name=canonical_name,
                version=dataset_version,
                content_hash=content_hash,
            ),
        )
    return outputs


def build_gfs_wave12_panel_non_sensitive(
    wave_paths: list[Path],
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    rows: list[dict[str, object]] = []
    for wave_path in sorted(wave_paths, key=lambda item: item.name):
        for row in score_gfs_rows(_read_rows(wave_path)):
            rows.append(
                {
                    "respondent_id": row["respondent_id"],
                    "wave": int(row["wave"]),
                    "country": row["country"],
                    "sampling_weight": float(row["weight"]),
                    "happiness": float(row["happiness"]),
                    "health": float(row["health"]),
                    "meaning": float(row["meaning"]),
                    "character": float(row["character"]),
                    "relationships": float(row["relationships"]),
                    "financial": float(row["financial"]),
                    "flourish_index_10": float(row["flourish_index_10"]),
                    "secure_flourish_index_12": float(row["secure_flourish_index_12"]),
                    "sensitive_data_included": False,
                    "measurement_mode": "longitudinal_research_grade",
                }
            )
    content_hash = sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.gfs_wave12_panel_non_sensitive-{content_hash}.parquet"
    reference = DatasetReferenceModel(
        canonical_dataset_name="features.gfs_wave12_panel_non_sensitive",
        version=dataset_version,
        content_hash=content_hash,
    )
    reference_text = f"({reference.canonical_dataset_name}, {reference.version}, {reference.content_hash})"
    rows = [{**row, "dataset_reference": reference_text} for row in rows]
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, reference


def build_gfs_wave12_marginals_country(
    panel_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> dict[str, tuple[Path, DatasetReferenceModel]]:
    rows = pq.read_table(panel_path).to_pylist()
    grouped: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(
        lambda: {
            "flourish_index_10": [],
            "secure_flourish_index_12": [],
            **{domain: [] for domain in DOMAIN_FIELDS},
        }
    )
    for row in rows:
        weight = float(row["sampling_weight"])
        for field in grouped[row["country"]]:
            grouped[row["country"]][field].append((float(row[field]), weight))

    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, tuple[Path, DatasetReferenceModel]] = {}
    for country, fields in sorted(grouped.items()):
        canonical_name = f"features.gfs_wave12_marginals_country_{country.lower()}"
        measures = [
            {
                "country": country,
                "measure": measure,
                "weighted_mean": round(_weighted_mean(values), 6),
                "sampling_weighted": True,
                "measurement_mode": "longitudinal_research_grade",
            }
            for measure, values in fields.items()
        ]
        content_hash = sha256(
            json.dumps(measures, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        reference = DatasetReferenceModel(
            canonical_dataset_name=canonical_name,
            version=dataset_version,
            content_hash=content_hash,
        )
        out_rows = [
            {
                **row,
                "dataset_reference": (
                    f"({reference.canonical_dataset_name}, {reference.version}, "
                    f"{reference.content_hash})"
                ),
            }
            for row in measures
        ]
        output_path = output_dir / f"{canonical_name}-{content_hash}.parquet"
        pq.write_table(pa.Table.from_pylist(out_rows), output_path)
        outputs[country] = (output_path, reference)
    return outputs
