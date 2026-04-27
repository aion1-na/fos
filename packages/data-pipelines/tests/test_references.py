from __future__ import annotations

from pathlib import Path

from fos_data_pipelines import ConnectorConfig, RawZone, build_fixture_reference
from fos_data_pipelines.dagster_assets import land_raw_fixture
from fos_data_pipelines.models import FeatureTable, HarmonizedArtifact, StagedArtifact


def test_fixture_reference_is_content_addressed(tmp_path: Path) -> None:
    fixture = tmp_path / "sample.csv"
    fixture.write_text("id,value\n1,fixture\n", encoding="utf-8")

    reference = build_fixture_reference(fixture, "fixture.sample", "0.1.0")

    assert reference.as_tuple() == (
        "fixture.sample",
        "0.1.0",
        "622aa93bd19fc2d4d6163edd26631edba5df379574feba07dab62bc822254f17",
    )


def test_same_raw_file_lands_to_same_hash_path_twice(tmp_path: Path) -> None:
    fixture = tmp_path / "sample.csv"
    fixture.write_text("id,value\n1,fixture\n", encoding="utf-8")
    raw_zone = RawZone(tmp_path / "raw-zone", uri_prefix="s3://minio/fos-raw")
    config = ConnectorConfig(
        connector_name="fixture_connector",
        connector_version="0.1.0",
        canonical_dataset_name="fixture.sample",
        dataset_version="2026-04-fixture",
        access_mode="fixture",
        source_uri="fixture://sample.csv",
        license_ref="docs/data/datasets/gfs.md#license-metadata",
        codebook_ref="docs/data/datasets/gfs.md#codebook-mapping",
        quality_profile_ref="docs/data/datasets/gfs.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/gfs.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/gfs.md#access-policy",
    )

    first = raw_zone.land_file(fixture, config)
    second = raw_zone.land_file(fixture, config)

    assert first.storage_path == second.storage_path
    assert first.artifact.content_hash == second.artifact.content_hash
    assert first.artifact.raw_uri == second.artifact.raw_uri
    assert first.artifact.dataset_reference.as_tuple() == (
        "fixture.sample",
        "2026-04-fixture",
        "622aa93bd19fc2d4d6163edd26631edba5df379574feba07dab62bc822254f17",
    )


def test_dagster_asset_skeleton_lands_raw_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "asset.csv"
    fixture.write_text("id,value\n1,asset\n", encoding="utf-8")
    config = ConnectorConfig(
        connector_name="asset_connector",
        connector_version="0.1.0",
        canonical_dataset_name="fixture.asset",
        dataset_version="2026-04-fixture",
        access_mode="fixture",
        source_uri="fixture://asset.csv",
        license_ref="docs/data/datasets/gfs.md#license-metadata",
        codebook_ref="docs/data/datasets/gfs.md#codebook-mapping",
        quality_profile_ref="docs/data/datasets/gfs.md#quality-profile",
        provenance_manifest_ref="docs/data/datasets/gfs.md#provenance-manifest",
        access_policy_ref="docs/data/datasets/gfs.md#access-policy",
    )

    artifact = land_raw_fixture(fixture, config, RawZone(tmp_path / "raw-zone"))

    assert getattr(land_raw_fixture, "__fos_asset__") is True
    assert artifact.connector_name == "asset_connector"
    assert artifact.raw_uri.startswith("s3://fos-raw/raw/fixture.asset/")


def test_artifact_schemas_carry_dataset_reference() -> None:
    staged = StagedArtifact(
        artifact_id="staged:fixture",
        raw_artifact_id="raw:fixture",
        stage_uri="s3://fos-stage/fixture.parquet",
        schema_version="0.1.0",
        row_count=1,
        transform_ref="docs/data/transforms/fixture.md",
    )
    harmonized = HarmonizedArtifact(
        artifact_id="harmonized:fixture",
        staged_artifact_id=staged.artifact_id,
        harmonized_uri="s3://fos-harmonized/fixture.parquet",
        schema_version="0.1.0",
        codebook_mapping_ref="docs/data/datasets/gfs.md#codebook-mapping",
        quality_profile_ref="docs/data/datasets/gfs.md#quality-profile",
    )
    feature_table = FeatureTable(
        table_id="features:fixture",
        harmonized_artifact_id=harmonized.artifact_id,
        feature_table_uri="s3://fos-features/fixture.parquet",
        schema_version="0.1.0",
        dataset_reference={
            "canonical_dataset_name": "fixture.sample",
            "version": "2026-04-fixture",
            "content_hash": "622aa93bd19fc2d4d6163edd26631edba5df379574feba07dab62bc822254f17",
        },
        intended_use="simulation",
    )

    assert feature_table.dataset_reference.as_tuple()[0] == "fixture.sample"
