from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.csv as csv
import pyarrow.compute as pc
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

VALID_JOIN_LEVELS = {"county", "zip", "tract", "national", "country"}
VALID_PATHWAY_ROLES = {"calibration", "validation"}
FEATURE_CODEBOOK_VERSION = "0.1"
CELL_SUPPRESSION_THRESHOLD = 10
SENSITIVE_CONTEXT_FIELDS = {
    "address",
    "date_of_birth",
    "household_id",
    "name",
    "person_id",
    "restricted_person_id",
    "ssn",
}
SUPPRESSION_METADATA_COLUMNS = {"year", "cell_count"}


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _request_status_payload(
    canonical_dataset_name: str,
    *,
    reason: str,
    source_path: Path,
    row_count: int,
) -> dict[str, object]:
    content_hash = sha256(
        json.dumps(
            {
                "canonical_dataset_name": canonical_dataset_name,
                "reason": reason,
                "row_count": row_count,
                "source_path": source_path.name,
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    return {
        "canonical_dataset_name": canonical_dataset_name,
        "dataset_version": "request-status-v0.1",
        "content_hash": content_hash,
        "dataset_reference": {
            "canonical_dataset_name": canonical_dataset_name,
            "version": "request-status-v0.1",
            "content_hash": content_hash,
        },
        "access_status": "request_status_stub",
        "reason": reason,
        "source_path": source_path.name,
        "row_count": row_count,
        "rows": [],
        "allowed_output": "request-status metadata only",
    }


def _write_request_status_payload(output_dir: Path, payload: dict[str, object]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{payload['canonical_dataset_name']}-request-status.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _assert_context_policy_columns(field_names: set[str]) -> None:
    sensitive_fields = sorted(SENSITIVE_CONTEXT_FIELDS & {name.lower() for name in field_names})
    if sensitive_fields:
        raise ValueError(f"context outputs cannot include sensitive fields: {sensitive_fields}")


def _write_feature(
    source_path: Path,
    output_dir: Path,
    canonical_dataset_name: str,
    dataset_version: str,
    *,
    pathway_role: str = "calibration",
) -> tuple[Path, DatasetReferenceModel]:
    table = csv.read_csv(source_path)
    _assert_context_policy_columns(set(table.column_names))
    original_row_count = table.num_rows
    valid_join = pc.and_kleene(
        pc.field("join_allowed"),
        pc.is_in(pc.field("geography_level"), value_set=pa.array(sorted(VALID_JOIN_LEVELS))),
    )
    table = table.filter(valid_join)
    if "pathway_role" in table.column_names:
        role_allowed = pc.is_in(
            pc.field("pathway_role"),
            value_set=pa.array(sorted(VALID_PATHWAY_ROLES)),
        )
        table = table.filter(role_allowed)
    if "join_key" not in table.column_names:
        table = table.append_column(
            "join_key",
            pa.array([_join_key_for_level(str(level)) for level in table["geography_level"].to_pylist()]),
        )
    else:
        expected_join_keys = pa.array(
            [_join_key_for_level(str(level)) for level in table["geography_level"].to_pylist()]
        )
        valid_join_key = pc.equal(
            table["join_key"],
            expected_join_keys,
        )
        table = table.filter(valid_join_key)
    invalid_row_count = original_row_count - table.num_rows
    if invalid_row_count:
        _write_request_status_payload(
            output_dir,
            _request_status_payload(
                f"{canonical_dataset_name}.unsupported_or_restricted_rows",
                reason="unsupported, restricted, or invalid geography join rows were excluded from the feature table",
                source_path=source_path,
                row_count=invalid_row_count,
            ),
        )
    if "join_segment" not in table.column_names:
        table = table.append_column(
            "join_segment",
            pa.array(["all" for _ in range(table.num_rows)]),
        )
    if "pathway_role" not in table.column_names:
        table = table.append_column(
            "pathway_role",
            pa.array([pathway_role for _ in range(table.num_rows)]),
        )
    table = table.append_column(
        "causal_interpretation",
        pa.array(["not_causal_proof" for _ in range(table.num_rows)]),
    )
    if "cell_count" in table.column_names:
        suppressed = pc.less(table["cell_count"], CELL_SUPPRESSION_THRESHOLD)
        table = table.append_column("suppressed", suppressed)
        for column_name in table.column_names:
            if column_name in SUPPRESSION_METADATA_COLUMNS:
                continue
            column = table[column_name]
            if not (pa.types.is_integer(column.type) or pa.types.is_floating(column.type)):
                continue
            table = table.set_column(
                table.schema.get_field_index(column_name),
                column_name,
                pc.if_else(suppressed, None, column),
            )
    else:
        table = table.append_column(
            "suppressed",
            pa.array([False for _ in range(table.num_rows)]),
        )
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


def _join_key_for_level(level: str) -> str:
    return {
        "county": "county_fips",
        "zip": "zip_code",
        "tract": "census_tract",
        "national": "country_iso3",
        "country": "country_iso3",
    }.get(level, "unsupported")


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
        pathway_role="calibration",
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
        pathway_role="calibration",
    )


def build_place_context(
    fixture_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    return _write_feature(
        fixture_path,
        output_dir,
        "features.place_context",
        dataset_version,
        pathway_role="calibration",
    )


def load_request_status_stub(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("access_status") != "request_status_stub":
        raise ValueError(f"{path} is not a request-status stub")
    if payload.get("rows") != []:
        raise ValueError(f"{path} must not include table rows before access is approved")
    for required in ["dataset_version", "content_hash", "dataset_reference"]:
        if required not in payload:
            raise ValueError(f"{path} is missing request-status provenance field: {required}")
    return payload
