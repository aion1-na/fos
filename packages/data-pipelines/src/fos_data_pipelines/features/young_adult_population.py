from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from fos_data_pipelines.models import DatasetReferenceModel

FEATURE_NAME = "features.us_young_adult_population_marginals"
DIAGNOSTICS_NAME = "features.synthetic_population_calibration_diagnostics"


def build_us_young_adult_population_marginals(
    marginal_bundle_path: Path,
    output_dir: Path,
    *,
    dataset_version: str,
) -> tuple[Path, DatasetReferenceModel]:
    payload: dict[str, Any] = json.loads(marginal_bundle_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = dict(payload)
    candidate["feature_table"] = FEATURE_NAME
    candidate["dataset_reference"] = {
        "canonical_dataset_name": FEATURE_NAME,
        "version": dataset_version,
        "content_hash": "0" * 64,
    }
    encoded = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode("utf-8")
    content_hash = sha256(encoded).hexdigest()
    candidate["dataset_reference"]["content_hash"] = content_hash
    final = (json.dumps(candidate, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    final_hash = sha256(final).hexdigest()
    candidate["dataset_reference"]["content_hash"] = final_hash
    final = (json.dumps(candidate, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )
    output_path = output_dir / f"{FEATURE_NAME}-{final_hash}.json"
    output_path.write_bytes(final)
    return (
        output_path,
        DatasetReferenceModel(
            canonical_dataset_name=FEATURE_NAME,
            version=dataset_version,
            content_hash=final_hash,
        ),
    )
