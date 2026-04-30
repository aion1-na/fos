from __future__ import annotations

import csv
import json
import os
from hashlib import sha256
from pathlib import Path
from typing import Any

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.common import rows_to_staged_parquet
from fos_data_pipelines.models import AccessMode, ConnectorConfig, DatasetReferenceModel, StagedArtifact

CONNECTOR_NAME = "gfs_cos_osf_connector"
CONNECTOR_VERSION = "0.2.0"
SUPPORTED_WAVES = (1, 2)
SENSITIVE_FIELDS = frozenset(
    {
        "name",
        "email",
        "phone",
        "address",
        "birth_date",
        "birthdate",
        "latitude",
        "longitude",
        "geocode",
        "postal_code",
        "ip_address",
        "contact_permission",
        "school_name",
        "employer_name",
        "sensitive_module",
    }
)


class SensitiveDataAccessError(PermissionError):
    """Raised when a GFS ingest attempts to expose sensitive or restricted fields."""


def _wave_slug(wave: int) -> str:
    if wave not in SUPPORTED_WAVES:
        raise ValueError(f"GFS Wave {wave} is not configured for non-sensitive ingest")
    return f"gfs-wave{wave}"


def _source_path(source_uri: str) -> Path | None:
    if source_uri.startswith("file://"):
        return Path(source_uri.removeprefix("file://"))
    if source_uri.startswith("/") or source_uri.startswith("."):
        return Path(source_uri)
    return None


def _is_fixture_source(path: Path) -> bool:
    return any("fixture" in part for part in path.parts)


def _approved_access_policy_exists(path: Path) -> bool:
    return path.with_suffix(path.suffix + ".access-approved.json").exists()


def _access_mode_for_source(source_uri: str) -> AccessMode:
    path = _source_path(source_uri)
    if path is not None and path.exists():
        if _is_fixture_source(path):
            return AccessMode.FIXTURE
        if _approved_access_policy_exists(path):
            return AccessMode.APPROVED_PRODUCTION
        return AccessMode.REQUEST_STATUS_STUB
    return AccessMode.REQUEST_STATUS_STUB


def gfs_connector_config(
    source_uri: str | None = None,
    *,
    wave: int = 1,
    dataset_version: str | None = None,
) -> ConnectorConfig:
    slug = _wave_slug(wave)
    source_uri = source_uri or os.environ.get(
        f"GFS_WAVE{wave}_NON_SENSITIVE_URI",
        f"osf+cos://registration-required/{slug}/non-sensitive",
    )
    access_mode = _access_mode_for_source(source_uri)
    resolved_version = dataset_version or {
        AccessMode.APPROVED_PRODUCTION: "1.0.0",
        AccessMode.FIXTURE: "fixture-0.1",
        AccessMode.REQUEST_STATUS_STUB: "request-status-v0.1",
    }[access_mode]
    return ConnectorConfig(
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
        canonical_dataset_name=f"gfs_wave{wave}",
        dataset_version=resolved_version,
        access_mode=access_mode,
        source_uri=source_uri,
        license_ref=f"docs/data/datasets/{slug}.md#license-metadata",
        codebook_ref=f"codebooks/gfs_wave{wave}.yaml",
        quality_profile_ref=f"docs/data/datasets/{slug}.md#quality-profile",
        provenance_manifest_ref=f"docs/data/datasets/{slug}.md#provenance-manifest",
        access_policy_ref=f"docs/data/datasets/{slug}.md#access-policy",
    )


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))


def assert_gfs_non_sensitive_rows(
    rows: list[dict[str, object]],
    *,
    approved_sensitive: bool = False,
) -> None:
    if not rows:
        return
    sensitive = SENSITIVE_FIELDS.intersection(rows[0])
    if sensitive and not approved_sensitive:
        raise SensitiveDataAccessError(
            f"GFS sensitive fields require approved access policy: {', '.join(sorted(sensitive))}"
        )


def parse_gfs_wave_fixture(
    fixture_path: Path,
    codebook_path: Path,
    output_dir: Path,
    *,
    wave: int,
) -> StagedArtifact:
    rows = _read_csv_rows(fixture_path)
    assert_gfs_non_sensitive_rows(rows)
    codebook = load_codebook(codebook_path)
    return rows_to_staged_parquet(
        rows,
        fixture_path=fixture_path,
        codebook=codebook,
        output_dir=output_dir,
        connector_name=CONNECTOR_NAME,
        connector_version=CONNECTOR_VERSION,
    )


def parse_gfs_wave1_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    return parse_gfs_wave_fixture(fixture_path, codebook_path, output_dir, wave=1)


def parse_gfs_wave2_fixture(fixture_path: Path, codebook_path: Path, output_dir: Path) -> StagedArtifact:
    return parse_gfs_wave_fixture(fixture_path, codebook_path, output_dir, wave=2)


def build_gfs_request_status_stub(
    *,
    wave: int | str,
    request_scope: str,
    dataset_version: str = "request-status-v0.1",
) -> dict[str, Any]:
    payload = {
        "canonical_dataset_name": f"gfs_wave{wave}" if isinstance(wave, int) else f"gfs_{wave}",
        "dataset_version": dataset_version,
        "access_status": "request_status_stub",
        "license_status": "not_approved",
        "registration_required": True,
        "source_system": "GFS COS/OSF approved portal",
        "request_scope": request_scope,
        "sensitive_data_access": False,
        "rows": [],
    }
    content_hash = __import__("hashlib").sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()
    payload["dataset_reference"] = DatasetReferenceModel(
        canonical_dataset_name=str(payload["canonical_dataset_name"]),
        version=dataset_version,
        content_hash=content_hash,
    ).model_dump(mode="json")
    payload["content_hash"] = content_hash
    return payload


def acquire_gfs_non_sensitive_source(config: ConnectorConfig) -> dict[str, Any]:
    """Resolve approved local GFS bytes or return request-status metadata without rows."""

    if config.access_mode != AccessMode.APPROVED_PRODUCTION:
        return build_gfs_request_status_stub(
            wave=config.canonical_dataset_name.removeprefix("gfs_wave"),
            request_scope=f"{config.canonical_dataset_name} non-sensitive microdata",
            dataset_version=config.dataset_version,
        )

    path = _source_path(config.source_uri)
    if path is None or not path.exists() or not _approved_access_policy_exists(path):
        raise PermissionError("approved GFS local source requires access-approved sidecar metadata")
    rows = _read_csv_rows(path)
    assert_gfs_non_sensitive_rows(rows)
    content_hash = sha256(path.read_bytes()).hexdigest()
    return {
        "canonical_dataset_name": config.canonical_dataset_name,
        "dataset_version": config.dataset_version,
        "access_status": config.access_mode.value,
        "source_uri": config.source_uri,
        "row_count": len(rows),
        "content_hash": content_hash,
        "dataset_reference": DatasetReferenceModel(
            canonical_dataset_name=config.canonical_dataset_name,
            version=config.dataset_version,
            content_hash=content_hash,
        ).model_dump(mode="json"),
    }
