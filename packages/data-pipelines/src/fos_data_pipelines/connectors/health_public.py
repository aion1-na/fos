from __future__ import annotations

from fos_data_pipelines.models import ConnectorConfig

CONNECTOR_VERSION = "0.1.0"


def _config(
    *,
    connector_name: str,
    canonical_dataset_name: str,
    source_uri: str,
    codebook_ref: str,
    dataset_card: str,
) -> ConnectorConfig:
    return ConnectorConfig(
        connector_name=connector_name,
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name=canonical_dataset_name,
        dataset_version="request-status-v0.1",
        source_uri=source_uri,
        license_ref=f"{dataset_card}#license-metadata",
        codebook_ref=codebook_ref,
        quality_profile_ref=f"{dataset_card}#quality-profile",
        provenance_manifest_ref=f"{dataset_card}#provenance-manifest",
        access_policy_ref=f"{dataset_card}#access-policy",
    )


def brfss_public_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="brfss_public",
        canonical_dataset_name="brfss_public",
        source_uri=source_uri,
        codebook_ref="codebooks/brfss_public.yaml",
        dataset_card="docs/data/datasets/brfss-public.md",
    )


def cdc_wonder_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="cdc_wonder_public_tables",
        canonical_dataset_name="cdc_public_health",
        source_uri=source_uri,
        codebook_ref="codebooks/cdc_public_health.yaml",
        dataset_card="docs/data/datasets/cdc-public-health.md",
    )
