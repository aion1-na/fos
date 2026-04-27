from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Literal

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, ConfigDict, Field

from fos_data_pipelines.models import DatasetReferenceModel


class PartnerFeedContract(BaseModel):
    model_config = ConfigDict(frozen=True)

    canonical_dataset_name: str
    connector_name: str
    connector_version: str
    license_compartment: str = Field(pattern=r"^commercial/[a-z0-9_-]+$")
    access_status: Literal["request_status_stub", "approved"] = "request_status_stub"
    license_status: Literal["not_approved", "approved"] = "not_approved"
    partition_grain: Literal["daily", "hourly"]
    snapshot_partition: str
    signal_family: Literal["job_postings", "hiring_velocity"]
    rows: list[dict[str, object]] = Field(default_factory=list)

    @property
    def ingest_allowed(self) -> bool:
        return self.access_status == "approved" and self.license_status == "approved"


def load_partner_feed_contracts(path: Path) -> list[PartnerFeedContract]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    contracts = [PartnerFeedContract.model_validate(item) for item in payload]
    for contract in contracts:
        if contract.rows:
            raise ValueError(f"{contract.canonical_dataset_name} must not include feed rows")
        if contract.ingest_allowed:
            raise ValueError(f"{contract.canonical_dataset_name} unexpectedly allows ingest")
    return contracts


def build_real_time_labor_signals(
    contracts_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "request-status-v0.1",
) -> tuple[Path, DatasetReferenceModel]:
    contracts = load_partner_feed_contracts(contracts_path)
    content_hash = sha256(contracts_path.read_bytes()).hexdigest()
    rows = [
        {
            "canonical_dataset_name": contract.canonical_dataset_name,
            "feature_table": "features.real_time_labor_signals",
            "dataset_reference": (
                f"(features.real_time_labor_signals, {dataset_version}, {content_hash})"
            ),
            "connector_name": contract.connector_name,
            "connector_version": contract.connector_version,
            "license_compartment": contract.license_compartment,
            "access_status": contract.access_status,
            "license_status": contract.license_status,
            "partition_grain": contract.partition_grain,
            "snapshot_partition": contract.snapshot_partition,
            "signal_family": contract.signal_family,
            "content_hash": content_hash,
            "pinnable_by_run_manifest": True,
            "secret_free_contract_test": True,
        }
        for contract in contracts
    ]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.real_time_labor_signals-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.real_time_labor_signals",
        version=dataset_version,
        content_hash=content_hash,
    )
