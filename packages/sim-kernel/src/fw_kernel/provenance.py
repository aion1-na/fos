from __future__ import annotations

import hashlib
import json
from typing import Any

from fw_contracts import DatasetReference, RunDataManifest
from fw_kernel.state import ColumnarState, state_to_jsonable


def tick_hash(tick: int, state: ColumnarState, kpis: dict[str, float]) -> str:
    payload = {
        "tick": tick,
        "state": state_to_jsonable(state),
        "kpis": {name: kpis[name] for name in sorted(kpis)},
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


DATASET_INPUT_KEYS = frozenset(
    {
        "dataset_path",
        "dataset_uri",
        "feature_table_path",
        "feature_table_uri",
        "raw_data_path",
        "raw_data_uri",
        "reference_path",
        "reference_uri",
    }
)
RUN_DATA_COMPONENTS = (
    "population_synthesis",
    "transition_models",
    "validation",
    "mirofish_adapter",
)


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def collect_dataset_references(*payloads: dict[str, Any]) -> list[DatasetReference]:
    references: dict[tuple[str, str, str], DatasetReference] = {}
    for payload in payloads:
        for raw_reference in payload.get("dataset_references", []):
            reference = DatasetReference.model_validate(raw_reference)
            references[reference.as_tuple()] = reference
    return [references[key] for key in sorted(references)]


def reject_unversioned_dataset_reads(*payloads: dict[str, Any]) -> None:
    for payload in payloads:
        for key, value in payload.items():
            if key in DATASET_INPUT_KEYS and value:
                raise ValueError(
                    f"{key} is an unversioned dataset read; use dataset_references "
                    "with canonical_dataset_name, version, and content_hash"
                )


def run_data_manifest(
    *,
    run_id: str,
    scenario_id: str,
    population_id: str,
    dataset_references: list[DatasetReference],
    branch_id: str | None = None,
    parent_branch_id: str | None = None,
) -> RunDataManifest:
    payload = {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "population_id": population_id,
        "dataset_references": [
            reference.model_dump(mode="json") for reference in dataset_references
        ],
        "touched_components": list(RUN_DATA_COMPONENTS),
        "branch_id": branch_id,
        "parent_branch_id": parent_branch_id,
    }
    return RunDataManifest(
        **payload,
        manifest_hash=_stable_hash(payload),
    )
