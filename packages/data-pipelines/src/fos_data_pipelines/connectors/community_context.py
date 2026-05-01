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


def parse_request_status_stub(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("access_status") != "request_status_stub":
        raise ValueError(f"{path} is not a request-status stub")
    if payload.get("rows", []) != []:
        raise ValueError(f"{path} must not include source rows before access is approved")
    for required in ["dataset_version", "content_hash", "dataset_reference"]:
        if required not in payload:
            raise ValueError(f"{path} is missing request-status provenance field: {required}")
    return payload


def gss_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="gss",
        canonical_dataset_name="gss_public_context",
        source_uri=source_uri,
        codebook_ref="codebooks/gss_public_context.yaml",
        dataset_card="docs/data/datasets/gss-public-context.md",
    )


def atus_public_time_use_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="atus_public_time_use",
        canonical_dataset_name="atus_public_time_use",
        source_uri=source_uri,
        codebook_ref="codebooks/atus_public_time_use.yaml",
        dataset_card="docs/data/datasets/atus-public-time-use.md",
    )


def pew_religious_landscape_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="pew_religious_landscape",
        canonical_dataset_name="pew_religious_landscape",
        source_uri=source_uri,
        codebook_ref="codebooks/pew_religious_landscape.yaml",
        dataset_card="docs/data/datasets/pew-religious-landscape.md",
    )


def volunteering_civic_life_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="volunteering_civic_life",
        canonical_dataset_name="volunteering_civic_life",
        source_uri=source_uri,
        codebook_ref="codebooks/volunteering_civic_life.yaml",
        dataset_card="docs/data/datasets/volunteering-civic-life.md",
    )


def social_capital_atlas_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="social_capital_atlas",
        canonical_dataset_name="social_capital_atlas",
        source_uri=source_uri,
        codebook_ref="codebooks/social_capital_atlas.yaml",
        dataset_card="docs/data/datasets/social-capital-atlas.md",
    )


def opportunity_atlas_connector_config(source_uri: str) -> ConnectorConfig:
    return _config(
        connector_name="opportunity_atlas",
        canonical_dataset_name="opportunity_atlas",
        source_uri=source_uri,
        codebook_ref="codebooks/opportunity_atlas.yaml",
        dataset_card="docs/data/datasets/opportunity-atlas.md",
    )
