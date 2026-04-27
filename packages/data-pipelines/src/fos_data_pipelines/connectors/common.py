from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.codebooks import Codebook
from fos_data_pipelines.models import StagedArtifact


def source_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def rows_to_staged_parquet(
    rows: Iterable[dict[str, object]],
    *,
    fixture_path: Path,
    codebook: Codebook,
    output_dir: Path,
    connector_name: str,
    connector_version: str,
) -> StagedArtifact:
    mapped_rows: list[dict[str, object]] = []
    for row in rows:
        mapped_rows.append(
            {
                field.canonical_name: row.get(field.source_field)
                for field in codebook.fields
                if field.source_field in row
            }
        )
    table = pa.Table.from_pylist(mapped_rows)
    content_hash = source_hash(fixture_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_path = output_dir / f"{codebook.canonical_dataset_name}-{content_hash}.parquet"
    pq.write_table(table, parquet_path)
    return StagedArtifact(
        artifact_id=f"staged:{codebook.canonical_dataset_name}:{content_hash}",
        raw_artifact_id=f"raw:{codebook.canonical_dataset_name}:{content_hash}",
        stage_uri=parquet_path.as_uri(),
        schema_version=codebook.version,
        row_count=table.num_rows,
        transform_ref=f"{connector_name}@{connector_version}",
    )
