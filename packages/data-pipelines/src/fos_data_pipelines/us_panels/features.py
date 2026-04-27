from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

US_PANEL_CONSTRUCTS = (
    "employment_status",
    "income",
    "health",
    "depression_wellbeing",
    "household",
    "demographics",
)


def load_registration_stub(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload["access_status"] != "request_status_stub":
        raise ValueError(f"{path} is not a request-status stub")
    if payload["license_status"] != "not_approved":
        raise ValueError(f"{path} must stay blocked until license approval")
    if payload["rows"] != []:
        raise ValueError(f"{path} must not contain restricted panel rows")
    return payload


def load_panel_codebook(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for panel, mapping in payload["panels"].items():
        missing = set(US_PANEL_CONSTRUCTS) - set(mapping)
        if missing:
            raise ValueError(f"{panel} missing canonical mappings: {sorted(missing)}")
    return payload


def _combined_hash(paths: list[Path]) -> str:
    digest = sha256()
    for path in sorted(paths, key=lambda item: item.name):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build_us_employment_wellbeing_panels(
    codebook_path: Path,
    wave_metadata_path: Path,
    quality_profiles_path: Path,
    stub_paths: list[Path],
    output_dir: Path,
    *,
    dataset_version: str = "request-status-v0.1",
) -> tuple[Path, DatasetReferenceModel]:
    codebook = load_panel_codebook(codebook_path)
    waves = json.loads(wave_metadata_path.read_text(encoding="utf-8"))
    profiles = json.loads(quality_profiles_path.read_text(encoding="utf-8"))
    stubs = [load_registration_stub(path) for path in stub_paths]
    rows: list[dict[str, object]] = []
    content_hash = _combined_hash([codebook_path, wave_metadata_path, quality_profiles_path, *stub_paths])
    for stub in stubs:
        panel = stub["canonical_dataset_name"]
        rows.append(
            {
                "canonical_dataset_name": panel,
                "feature_table": "features.us_employment_wellbeing_panels",
                "dataset_reference": (
                    f"(features.us_employment_wellbeing_panels, {dataset_version}, {content_hash})"
                ),
                "access_status": stub["access_status"],
                "license_status": stub["license_status"],
                "registration_required": stub["registration_required"],
                "constructs": list(US_PANEL_CONSTRUCTS),
                "source_variable_mapping": json.dumps(codebook["panels"][panel], sort_keys=True),
                "wave_metadata": json.dumps(waves[panel], sort_keys=True),
                "quality_profile": json.dumps(profiles[panel], sort_keys=True),
                "usable_by_training": True,
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.us_employment_wellbeing_panels-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.us_employment_wellbeing_panels",
        version=dataset_version,
        content_hash=content_hash,
    )
