from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.compute as pc
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

VALID_JOIN_LEVELS = {"county", "zip", "tract", "national"}
FEATURE_CODEBOOK_VERSION = "0.1"


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_feature(
    source_path: Path,
    output_dir: Path,
    canonical_dataset_name: str,
    dataset_version: str,
) -> tuple[Path, DatasetReferenceModel]:
    table = csv.read_csv(source_path)
    valid_join = pc.and_kleene(
        pc.field("join_allowed"),
        pc.is_in(pc.field("geography_level"), value_set=pa.array(sorted(VALID_JOIN_LEVELS))),
    )
    table = table.filter(valid_join)
    content_hash = _hash_file(source_path)
    table = table.append_column(
        "content_hash",
        pa.array([content_hash for _ in range(table.num_rows)]),
    )
    table = table.append_column(
        "codebook_version",
        pa.array([FEATURE_CODEBOOK_VERSION for _ in range(table.num_rows)]),
    )
    table = table.append_column(
        "dataset_reference",
        pa.array(
            [
                f"({canonical_dataset_name}, {dataset_version}, {content_hash})"
                for _ in range(table.num_rows)
            ]
        ),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{canonical_dataset_name}-{content_hash}.parquet"
    pq.write_table(table, output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name=canonical_dataset_name,
        version=dataset_version,
        content_hash=content_hash,
    )


def build_community_context(
    fixture_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    return _write_feature(
        fixture_path,
        output_dir,
        "features.community_context",
        dataset_version,
    )


def build_time_use_context(
    fixture_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    return _write_feature(
        fixture_path,
        output_dir,
        "features.time_use_context",
        dataset_version,
    )


def build_social_capital_context(
    fixture_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    return _write_feature(
        fixture_path,
        output_dir,
        "features.social_capital_context",
        dataset_version,
    )


def load_request_status_stub(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("access_status") != "request_status_stub":
        raise ValueError(f"{path} is not a request-status stub")
    if payload.get("rows") != []:
        raise ValueError(f"{path} must not include table rows before access is approved")
    return payload
