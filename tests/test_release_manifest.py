from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from fos_data_service.app import resolve_dataset

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "docs" / "data" / "releases" / "tier1-v1.0.0.json"
PROVENANCE = ROOT / "docs" / "data" / "releases" / "tier1-v1.0.0-provenance.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_release_manifest_has_required_lock_fields() -> None:
    manifest = _load(RELEASE)
    assert manifest["version"] == "1.0.0"
    assert manifest["datasets"]
    for dataset in manifest["datasets"]:
        for required in [
            "canonical_dataset_name",
            "version",
            "content_hash",
            "connector_name",
            "connector_version",
            "codebook_version",
            "license_class",
            "card_url",
            "artifact_uri",
        ]:
            assert dataset[required], (dataset["canonical_dataset_name"], required)
        assert re.fullmatch(r"[a-f0-9]{64}", dataset["content_hash"])
        assert (ROOT / dataset["card_url"]).exists()


def test_release_manifest_hashes_match_local_artifacts() -> None:
    manifest = _load(RELEASE)
    for dataset in manifest["datasets"]:
        artifact = ROOT / dataset["artifact_uri"]
        assert artifact.exists(), artifact
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        assert digest == dataset["content_hash"]


def test_fresh_environment_can_resolve_every_v1_dataset_reference() -> None:
    manifest = _load(RELEASE)
    for dataset in manifest["datasets"]:
        resolved = resolve_dataset(
            dataset["canonical_dataset_name"],
            dataset["version"],
            dataset["content_hash"],
        )
        assert "error" not in resolved
        assert resolved["dataset_reference"]["version"] == "1.0.0"
        assert resolved["manifest_path"] == manifest["provenance_manifest"]


def test_mvp_smoke_run_has_full_provenance_manifest() -> None:
    manifest = _load(RELEASE)
    provenance = _load(PROVENANCE)
    manifest_refs = {
        (
            dataset["canonical_dataset_name"],
            dataset["version"],
            dataset["content_hash"],
        )
        for dataset in manifest["datasets"]
    }
    smoke_refs = {tuple(reference) for reference in provenance["smoke_run"]["dataset_references"]}
    assert provenance["smoke_run"]["status"] == "succeeded"
    assert provenance["smoke_run"]["provenance_complete"] is True
    assert smoke_refs == manifest_refs


def test_retention_refetch_release_and_deployment_docs_exist() -> None:
    docs = [
        "docs/data/releases/immutable-artifact-retention.md",
        "docs/data/releases/tier1-v1.0.0-release-notes.md",
        "docs/data/runbooks/refetch-periodic-sources.md",
        "docs/data/runbooks/mvp-data-service-deployment.md",
    ]
    for relative in docs:
        content = (ROOT / relative).read_text(encoding="utf-8")
        assert "content" in content.lower() or "dataset reference" in content.lower()
        assert "1.0.0" in content or "pinned" in content.lower() or "deployment" in content.lower()


def test_tier2_dua_tracker_has_named_owners_and_dates() -> None:
    tracker = (ROOT / "docs" / "data" / "dua" / "tier2-submission-checklist.md").read_text(
        encoding="utf-8"
    )
    for dataset in ["HRS", "SOEP", "Understanding Society", "Census RDC", "Commercial labor data"]:
        assert dataset in tracker
    assert re.search(r"\d{4}-\d{2}-\d{2}", tracker)
    assert "Owner" in tracker
