from __future__ import annotations

import csv
import json
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

CELL_SUPPRESSION_THRESHOLD = 10
FEATURE_CODEBOOK_VERSION = "0.1"


def parse_public_health_stub(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("access_status") != "request_status_stub":
        raise ValueError(f"{path} is not a request-status stub")
    return payload


def build_health_validation_context(
    mortality_fixture: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    rows = []
    for row in csv.DictReader(mortality_fixture.read_text(encoding="utf-8").splitlines()):
        deaths = int(row["deaths"])
        suppressed = deaths < CELL_SUPPRESSION_THRESHOLD
        rows.append(
            {
                "source": row["source"],
                "source_country_code": row["country_code"],
                "country_iso3": "USA" if row["country_code"] == "US" else row["country_code"],
                "year": int(row["year"]),
                "age_group": row["age_group"],
                "deaths": None if suppressed else deaths,
                "population": int(row["population"]),
                "mortality_rate": None if suppressed else float(row["mortality_rate"]),
                "suppressed": suppressed,
                "suppression_rule": f"deaths < {CELL_SUPPRESSION_THRESHOLD}",
            }
        )
    content_hash = sha256(mortality_fixture.read_bytes()).hexdigest()
    dataset_reference = (
        f"(features.health_validation_context, {dataset_version}, {content_hash})"
    )
    rows = [
        {
            **row,
            "content_hash": content_hash,
            "codebook_version": FEATURE_CODEBOOK_VERSION,
            "dataset_reference": dataset_reference,
        }
        for row in rows
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.health_validation_context-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.health_validation_context",
        version=dataset_version,
        content_hash=content_hash,
    )
