from __future__ import annotations

import csv
import json
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

ISO3_BY_SOURCE_CODE = {
    "US": "USA",
    "USA": "USA",
    "JP": "JPN",
    "JPN": "JPN",
    "DE": "DEU",
    "DEU": "DEU",
}


def parse_international_public_stub(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_policy_regime_context(
    fixture_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    rows = []
    for row in csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines()):
        rows.append(
            {
                "source": row["source"],
                "source_country_code": row["source_country_code"],
                "country_iso3": ISO3_BY_SOURCE_CODE[row["source_country_code"]],
                "year": int(row["year"]),
                "indicator": row["indicator"],
                "value": float(row["value"]),
            }
        )
    content_hash = sha256(fixture_path.read_bytes()).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.policy_regime_context-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.policy_regime_context",
        version=dataset_version,
        content_hash=content_hash,
    )


def build_cross_country_dashboard_view(
    policy_context_path: Path,
    output_dir: Path,
) -> Path:
    rows = pq.read_table(policy_context_path).to_pylist()
    dashboard_rows = [
        {
            **row,
            "view_name": "atlas.cross_country_policy_dashboard",
            "queryable_with": "flourishing_and_employment_indicators",
        }
        for row in rows
    ]
    digest = sha256(policy_context_path.read_bytes()).hexdigest()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"atlas.cross_country_policy_dashboard-{digest}.parquet"
    pq.write_table(pa.Table.from_pylist(dashboard_rows), output_path)
    return output_path
