from __future__ import annotations

import json
from pathlib import Path

from fw_contracts import DatasetReference
from fos_data_service.app import dataset_lineage, resolve_dataset

ROOT = Path(__file__).resolve().parents[1]


def test_dataset_reference_contract_rejects_unversioned_reads() -> None:
    payload = resolve_dataset("features.community_context")
    assert payload["error"] == "dataset_reference_schema_break"


def test_dataset_reference_contract_resolves_full_content_address() -> None:
    reference = DatasetReference(
        canonical_dataset_name="features.community_context",
        version="fixture-0.1",
        content_hash="a" * 64,
    )
    payload = resolve_dataset(*reference.as_tuple())
    assert payload["dataset_reference"] == reference.model_dump(mode="json")


def test_platform_smoke_fixture_records_every_dataset_reference_touched() -> None:
    smoke_run = json.loads(
        (ROOT / "tests" / "fixtures" / "fdw_smoke_run.json").read_text(encoding="utf-8")
    )
    touched_references = [
        DatasetReference.model_validate(item) for item in smoke_run["dataset_references"]
    ]
    assert smoke_run["dataset_references"]
    for reference in touched_references:
        lineage = dataset_lineage(*reference.as_tuple())
        assert smoke_run["id"] in lineage["downstream"]


def test_api_run_manifest_records_all_simulation_data_components() -> None:
    from fos_api.main import _simulation_run_artifact

    artifact = _simulation_run_artifact("simulation-run-fdw-smoke")
    manifest = artifact["manifest"]["run_data_manifest"]

    assert artifact["manifest"]["dataset_references"] == manifest["dataset_references"]
    assert set(manifest["touched_components"]) == {
        "population_synthesis",
        "transition_models",
        "validation",
        "mirofish_adapter",
    }
    assert artifact["manifest"]["branch_data_manifests"]


def test_schema_breaks_return_structured_errors() -> None:
    payload = resolve_dataset("features.community_context", "fixture-0.1", "not-a-hash")
    assert payload["error"] == "dataset_reference_schema_break"


def test_missing_dataset_reference_returns_structured_error() -> None:
    payload = resolve_dataset("features.community_context", "fixture-9.9", "f" * 64)
    assert payload["error"] == "missing_dataset"
    assert "is not registered" in payload["message"]


def test_old_dataset_reference_versions_remain_resolvable() -> None:
    old_payload = resolve_dataset("features.community_context", "fixture-0.0", "b" * 64)
    new_payload = resolve_dataset("features.community_context", "fixture-0.1", "a" * 64)
    assert old_payload["dataset_reference"]["version"] == "fixture-0.0"
    assert new_payload["dataset_reference"]["version"] == "fixture-0.1"
