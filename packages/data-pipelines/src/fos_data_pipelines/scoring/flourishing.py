from __future__ import annotations

import csv
from collections import defaultdict
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

DOMAIN_FIELDS = ("happiness", "health", "meaning", "character", "relationships", "financial")


def _weighted_mean(values: list[tuple[float, float]]) -> float:
    numerator = sum(value * weight for value, weight in values)
    denominator = sum(weight for _, weight in values)
    if denominator == 0:
        raise ValueError("sampling weights must sum to a positive value")
    return numerator / denominator


def score_six_domain_country_marginals(fixture_path: Path) -> dict[str, dict[str, float]]:
    rows = list(csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()))
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
