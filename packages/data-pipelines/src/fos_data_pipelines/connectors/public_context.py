from __future__ import annotations

import json
from pathlib import Path

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


def parse_public_context_stub(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("access_status") not in {"request_status_stub", "public_metadata_stub"}:
        raise ValueError(f"{path} is not a public-context metadata stub")
    return payload


def world_happiness_report_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="world_happiness_report",
        canonical_dataset_name="world_happiness_report",
        source_uri=source_uri,
        codebook_ref="codebooks/world_happiness_report.yaml",
        dataset_card="docs/data/datasets/world-happiness-report.md",
    )


def ess_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="ess",
        canonical_dataset_name="ess",
        source_uri=source_uri,
        codebook_ref="codebooks/ess.yaml",
        dataset_card="docs/data/datasets/ess.md",
    )


def wvs_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="wvs",
        canonical_dataset_name="wvs",
        source_uri=source_uri,
        codebook_ref="codebooks/wvs.yaml",
        dataset_card="docs/data/datasets/wvs.md",
    )


def oecd_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="oecd",
        canonical_dataset_name="oecd_public_context",
        source_uri=source_uri,
        codebook_ref="codebooks/oecd_public_context.yaml",
        dataset_card="docs/data/datasets/oecd-public-context.md",
    )


def world_bank_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="world_bank",
        canonical_dataset_name="world_bank_public_context",
        source_uri=source_uri,
        codebook_ref="codebooks/world_bank_public_context.yaml",
        dataset_card="docs/data/datasets/world-bank-public-context.md",
    )


def eurostat_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="eurostat",
        canonical_dataset_name="eurostat_public_context",
        source_uri=source_uri,
        codebook_ref="codebooks/eurostat_public_context.yaml",
        dataset_card="docs/data/datasets/eurostat-public-context.md",
    )


def ilo_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="ilo",
        canonical_dataset_name="ilo_public_context",
        source_uri=source_uri,
        codebook_ref="codebooks/ilo_public_context.yaml",
        dataset_card="docs/data/datasets/ilo-public-context.md",
    )
