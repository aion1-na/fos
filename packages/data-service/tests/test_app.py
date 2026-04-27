from __future__ import annotations

from pathlib import Path

from fw_contracts import DatasetReference
from fos_data_pipelines.models import RawArtifact
from fos_data_service.app import (
    claim_lookup,
    dataset_card,
    dataset_lineage,
    dataset_manifest,
    dataset_policy,
    health,
    list_datasets,
    resolve_dataset,
)
from fos_data_service.catalog import Catalog, DatasetRecord


def test_health_is_metadata_only() -> None:
    assert health() == {"status": "ok", "service": "data-service"}


def test_dataset_listing_uses_request_status_stubs() -> None:
    datasets = list_datasets()["datasets"]
    assert datasets
    assert all(dataset["access_status"] == "request_status_stub" for dataset in datasets)


def test_catalog_tracks_connector_versions_separately_from_dataset_versions() -> None:
    catalog = Catalog()
    first = RawArtifact(
        artifact_id="raw:gfs:2026:v1",
        canonical_dataset_name="gfs",
        dataset_version="2026-fixture",
        connector_name="gfs_fixture",
        connector_version="0.1.0",
        content_hash="a" * 64,
        raw_uri="s3://fos-raw/raw/gfs/a.csv",
        byte_size=10,
    )
    second = first.model_copy(
        update={
            "artifact_id": "raw:gfs:2026:v2",
            "connector_version": "0.2.0",
            "content_hash": "b" * 64,
            "raw_uri": "s3://fos-raw/raw/gfs/b.csv",
        }
    )

    catalog.register_raw_artifact(first)
    catalog.register_raw_artifact(second)

    assert catalog.dataset_versions == {("gfs", "2026-fixture")}
    assert catalog.connector_versions == {("gfs_fixture", "0.1.0"), ("gfs_fixture", "0.2.0")}


def test_catalog_answers_artifact_lineage() -> None:
    catalog = Catalog()
    artifact = RawArtifact(
        artifact_id="raw:hrs:stub:v1",
        canonical_dataset_name="hrs",
        dataset_version="access-not-approved",
        connector_name="hrs_request_status",
        connector_version="0.1.0",
        content_hash="c" * 64,
        raw_uri="s3://fos-raw/raw/hrs/stub.json",
        byte_size=2,
    )

    catalog.register_raw_artifact(artifact)
    lineage = catalog.artifact_lineage("raw:hrs:stub:v1")

    assert lineage is not None
    assert lineage.dataset_version == "access-not-approved"
    assert lineage.connector_version == "0.1.0"


def test_catalog_rejects_production_ready_without_complete_policy_metadata() -> None:
    catalog = Catalog()
    try:
        catalog.register_dataset_policy(
            "gfs-wave1",
            tier="Tier 1",
            status="fixture",
            production_ready=True,
            metadata_fields={"License metadata:"},
        )
    except ValueError as exc:
        assert "cannot be production-ready" in str(exc)
    else:
        raise AssertionError("production-ready fixture without complete metadata was accepted")


def test_catalog_policy_endpoint_fails_closed_for_unknown_dataset() -> None:
    payload = dataset_policy("unknown")
    assert payload["policy"] is None
    assert payload["can_mark_production_ready"] is False


def test_resolve_requires_version_and_content_hash() -> None:
    payload = resolve_dataset("features.community_context")
    assert payload["error"] == "dataset_reference_schema_break"
    assert "canonical_dataset_name, version, and content_hash" in payload["message"]


def test_resolve_returns_card_and_manifest_for_full_reference() -> None:
    payload = resolve_dataset("features.community_context", "fixture-0.1", "a" * 64)
    assert payload["dataset_reference"]["canonical_dataset_name"] == "features.community_context"
    assert payload["dataset_reference"]["version"] == "fixture-0.1"
    assert payload["card_path"] == "docs/data/datasets/community-pathways.md"
    assert payload["manifest_path"] == "manifests/fixture-0.1/community-context.json"


def test_old_versions_remain_resolvable_after_new_version_is_registered() -> None:
    old_payload = resolve_dataset("features.community_context", "fixture-0.0", "b" * 64)
    new_payload = resolve_dataset("features.community_context", "fixture-0.1", "a" * 64)
    assert old_payload["dataset_reference"]["version"] == "fixture-0.0"
    assert new_payload["dataset_reference"]["version"] == "fixture-0.1"


def test_card_manifest_lineage_and_claim_lookup_endpoints() -> None:
    card = dataset_card("features.community_context", "fixture-0.1", "a" * 64)
    manifest = dataset_manifest("features.community_context", "fixture-0.1", "a" * 64)
    lineage = dataset_lineage("features.community_context", "fixture-0.1", "a" * 64)
    claim = claim_lookup("claim_mentoring_meaning_v0")
    assert card["card_path"] == "docs/data/datasets/community-pathways.md"
    assert manifest["dataset_reference"]["content_hash"] == "a" * 64
    assert lineage["downstream"] == ["simulation-run-fdw-smoke"]
    assert claim["dataset_references"][0]["canonical_dataset_name"] == "features.community_context"


def test_catalog_resolves_registered_dataset_reference_records() -> None:
    catalog = Catalog()
    reference = DatasetReference(
        canonical_dataset_name="features.time_use_context",
        version="fixture-0.1",
        content_hash="c" * 64,
    )
    catalog.register_dataset_record(
        DatasetRecord(
            reference=reference,
            card_path="docs/data/datasets/atus-public-time-use.md",
            manifest_path="manifests/fixture-0.1/time-use.json",
        )
    )
    assert catalog.resolve_dataset_reference(reference).reference == reference


def test_postgres_catalog_migration_declares_lineage_tables() -> None:
    migration = (
        Path(__file__).resolve().parents[1] / "migrations" / "001_catalog.sql"
    ).read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS connector_versions" in migration
    assert "CREATE TABLE IF NOT EXISTS dataset_versions" in migration
    assert "CREATE TABLE IF NOT EXISTS artifacts" in migration
    assert "connector_version TEXT NOT NULL" in migration
    assert "dataset_version TEXT NOT NULL" in migration
