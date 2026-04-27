from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel


@dataclass(frozen=True, slots=True)
class ReplicationArchive:
    canonical_dataset_name: str
    dataset_version: str
    source_citation: str
    content_hash: str
    file_hashes: dict[str, str]
    variable_labels: dict[str, str]
    source_variable_names: tuple[str, ...]


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def load_replication_archive(root: Path) -> ReplicationArchive:
    manifest = json.loads((root / "archive_manifest.json").read_text(encoding="utf-8"))
    file_hashes: dict[str, str] = {}
    digest = sha256()
    for file_entry in manifest["files"]:
        relative = file_entry["path"]
        content = (root / relative).read_bytes()
        file_hashes[relative] = sha256(content).hexdigest()
        digest.update(relative.encode("utf-8"))
        digest.update(content)

    dta_payload = json.loads((root / "china_shock_fixture.dta.json").read_text(encoding="utf-8"))
    source_variable_names = tuple(dta_payload["variable_labels"].keys())
    return ReplicationArchive(
        canonical_dataset_name=manifest["canonical_dataset_name"],
        dataset_version=manifest["dataset_version"],
        source_citation=manifest["source_citation"],
        content_hash=digest.hexdigest(),
        file_hashes=file_hashes,
        variable_labels=dta_payload["variable_labels"],
        source_variable_names=source_variable_names,
    )


def build_adh_china_shock_panel(archive_root: Path, output_dir: Path) -> tuple[Path, DatasetReferenceModel]:
    archive = load_replication_archive(archive_root)
    payload = json.loads((archive_root / "china_shock_fixture.dta.json").read_text(encoding="utf-8"))
    rows = [
        {
            **row,
            "raw_archive_hash": archive.content_hash,
            "source_citation": archive.source_citation,
            "source_variable_names": ",".join(archive.source_variable_names),
        }
        for row in payload["rows"]
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.adh_china_shock_panel-{archive.content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.adh_china_shock_panel",
        version=archive.dataset_version,
        content_hash=archive.content_hash,
    )


def _build_csv_feature(
    fixture_path: Path,
    output_dir: Path,
    canonical_dataset_name: str,
    raw_archive_hash: str,
) -> tuple[Path, DatasetReferenceModel]:
    rows = [
        {**row, "raw_archive_hash": raw_archive_hash}
        for row in csv.DictReader(fixture_path.read_text(encoding="utf-8").splitlines())
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    content_hash = sha256(fixture_path.read_bytes() + raw_archive_hash.encode("utf-8")).hexdigest()
    output_path = output_dir / f"{canonical_dataset_name}-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name=canonical_dataset_name,
        version="fixture-0.1",
        content_hash=content_hash,
    )


def build_pntr_mortality_backtest(
    fixture_path: Path, output_dir: Path, raw_archive_hash: str
) -> tuple[Path, DatasetReferenceModel]:
    return _build_csv_feature(
        fixture_path,
        output_dir,
        "features.pntr_mortality_backtest",
        raw_archive_hash,
    )


def build_robot_exposure_table(
    fixture_path: Path, output_dir: Path, raw_archive_hash: str
) -> tuple[Path, DatasetReferenceModel]:
    return _build_csv_feature(
        fixture_path,
        output_dir,
        "features.robot_exposure",
        raw_archive_hash,
    )


def validate_china_shock_gate(references: dict[str, str | None]) -> tuple[bool, list[str]]:
    required = [
        "features.adh_china_shock_panel",
        "raw_archive_hash",
        "connector_version",
        "source_citation",
        "stata_variable_label_manifest",
    ]
    missing = [key for key in required if not references.get(key)]
    return (not missing, missing)
