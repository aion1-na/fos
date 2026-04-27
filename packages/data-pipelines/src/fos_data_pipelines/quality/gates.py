from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.compute as pc
from pydantic import BaseModel, ConfigDict, Field

from fos_data_pipelines.quality.cards import lint_dataset_card


class QualityGateReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    canonical_dataset_name: str
    row_count: int = Field(ge=0)
    missingness: dict[str, int]
    distributions: dict[str, dict[str, int]]
    pii_candidates: list[str]
    sampling_metadata: dict[str, str]
    required_columns_present: bool


def load_tier1_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_expectation_suites(path: Path) -> dict[str, dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def _value_counts(table: pa.Table, column: str) -> dict[str, int]:
    values = table[column].to_pylist()
    counter = Counter("missing" if value is None else str(value) for value in values)
    return dict(sorted(counter.items()))


def run_quality_gate(
    canonical_dataset_name: str,
    table: pa.Table,
    expectation_suite: dict[str, Any],
    *,
    sampling_metadata: dict[str, str] | None = None,
) -> QualityGateReport:
    required_columns = set(expectation_suite.get("required_columns", []))
    present_columns = set(table.column_names)
    missingness = {
        column: int(pc.sum(pc.is_null(table[column])).as_py())
        for column in table.column_names
    }
    distributions = {
        column: _value_counts(table, column)
        for column in expectation_suite.get("distribution_columns", [])
        if column in present_columns
    }
    pii_candidates = [
        column
        for column in table.column_names
        if any(marker in column.lower() for marker in ("name", "email", "phone", "ssn"))
    ]
    declared_pii = list(expectation_suite.get("pii_candidates", []))
    return QualityGateReport(
        canonical_dataset_name=canonical_dataset_name,
        row_count=table.num_rows,
        missingness=missingness,
        distributions=distributions,
        pii_candidates=sorted(set(pii_candidates + declared_pii)),
        sampling_metadata=sampling_metadata or {},
        required_columns_present=required_columns.issubset(present_columns),
    )


def validate_tier1_release_candidate(
    manifest_path: Path,
    expectation_path: Path,
    repo_root: Path,
) -> list[str]:
    manifest = load_tier1_manifest(manifest_path)
    expectations = load_expectation_suites(expectation_path)
    defects: list[str] = []
    for dataset in manifest["datasets"]:
        name = dataset["canonical_dataset_name"]
        if name not in expectations:
            defects.append(f"{name}: missing expectation suite")
        card_path = repo_root / dataset["card_path"]
        if not card_path.exists():
            defects.append(f"{name}: missing dataset card")
            continue
        missing_fields = lint_dataset_card(card_path)
        if missing_fields:
            defects.append(f"{name}: missing card fields {', '.join(missing_fields)}")
        if dataset.get("production_ready") is True and missing_fields:
            defects.append(f"{name}: production-ready without complete metadata")
        if dataset.get("production_ready") is True and dataset.get("status") != "approved_production":
            defects.append(f"{name}: production-ready requires approved_production status")
    return defects
