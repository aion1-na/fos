from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from fos_data_pipelines.models import DatasetReferenceModel

CROSS_COUNTRY_CONSTRUCTS = (
    "employment",
    "education",
    "income",
    "family",
    "health",
    "wellbeing",
)


def _hash_paths(paths: list[Path]) -> str:
    digest = sha256()
    for path in sorted(paths, key=lambda item: item.name):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_international_panel_stubs(path: Path) -> list[dict[str, Any]]:
    panels = json.loads(path.read_text(encoding="utf-8"))
    for panel in panels:
        if panel["access_status"] != "request_status_stub":
            raise ValueError(f"{panel['canonical_dataset_name']} must remain request-status")
        if panel["license_status"] != "not_approved":
            raise ValueError(f"{panel['canonical_dataset_name']} cannot ingest before license approval")
        if panel["rows"] != []:
            raise ValueError(f"{panel['canonical_dataset_name']} must not contain panel rows")
        for required in ["country", "wave_metadata"]:
            if required not in panel:
                raise ValueError(f"{panel['canonical_dataset_name']} missing {required}")
        for required in ["waves", "weight_column", "sampling_design"]:
            if required not in panel["wave_metadata"]:
                raise ValueError(f"{panel['canonical_dataset_name']} missing wave_metadata.{required}")
    return panels


def build_cross_country_employment_wellbeing_panels(
    panel_stubs_path: Path,
    codebook_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "request-status-v0.1",
) -> tuple[Path, DatasetReferenceModel]:
    panels = load_international_panel_stubs(panel_stubs_path)
    codebook = json.loads(codebook_path.read_text(encoding="utf-8"))
    missing = set(CROSS_COUNTRY_CONSTRUCTS) - set(codebook["constructs"])
    if missing:
        raise ValueError(f"cross-country codebook missing constructs: {sorted(missing)}")
    content_hash = _hash_paths([panel_stubs_path, codebook_path])
    rows = []
    for panel in panels:
        rows.append(
            {
                "canonical_dataset_name": panel["canonical_dataset_name"],
                "feature_table": "features.cross_country_employment_wellbeing_panels",
                "dataset_reference": (
                    f"(features.cross_country_employment_wellbeing_panels, {dataset_version}, {content_hash})"
                ),
                "country": panel["country"],
                "coverage": panel["coverage"],
                "wave_metadata": json.dumps(panel["wave_metadata"], sort_keys=True),
                "weight_column": panel["wave_metadata"]["weight_column"],
                "sampling_design": panel["wave_metadata"]["sampling_design"],
                "constructs": list(CROSS_COUNTRY_CONSTRUCTS),
                "comparability": json.dumps(codebook["constructs"], sort_keys=True),
                "access_status": panel["access_status"],
                "license_status": panel["license_status"],
            }
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.cross_country_employment_wellbeing_panels-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.cross_country_employment_wellbeing_panels",
        version=dataset_version,
        content_hash=content_hash,
    )


def build_safety_net_regime_comparators(
    regimes_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    regimes = json.loads(regimes_path.read_text(encoding="utf-8"))
    content_hash = _hash_paths([regimes_path])
    rows = [
        {
            **row,
            "feature_table": "features.safety_net_regime_comparators",
            "dataset_reference": (
                f"(features.safety_net_regime_comparators, {dataset_version}, {content_hash})"
            ),
        }
        for row in regimes
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.safety_net_regime_comparators-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.safety_net_regime_comparators",
        version=dataset_version,
        content_hash=content_hash,
    )
