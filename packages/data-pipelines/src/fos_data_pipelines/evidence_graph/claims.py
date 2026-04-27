from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Literal

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel, ConfigDict, Field

from fos_data_pipelines.models import DatasetReferenceModel


class EvidenceSource(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(min_length=1)
    canonical_dataset_name: str = Field(min_length=1)
    access_status: Literal["request_status_stub", "fixture", "approved_production"]
    dataset_card: str = Field(min_length=1)
    provenance_manifest: str = Field(min_length=1)
    citation: str = Field(min_length=1)


class EvidenceClaim(BaseModel):
    model_config = ConfigDict(frozen=True)

    claim_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    estimate: float
    uncertainty: float = Field(ge=0)
    population: str = Field(min_length=1)
    treatment: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    confidence_label: Literal["draft", "advisor_reviewed", "rejected"]
    risk_of_bias: Literal["low", "medium", "high"]
    review_status: Literal["draft", "advisor_reviewed", "rejected"]
    provenance_link: str = Field(min_length=1)


def load_evidence_sources(path: Path) -> list[EvidenceSource]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [EvidenceSource.model_validate(item) for item in payload]


def load_evidence_claims(path: Path) -> list[EvidenceClaim]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [EvidenceClaim.model_validate(item) for item in payload]


def _combined_hash(paths: list[Path]) -> str:
    digest = sha256()
    for path in sorted(paths, key=lambda item: str(item)):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build_intervention_effect_size_priors(
    claims_path: Path,
    sources_path: Path,
    output_dir: Path,
    *,
    dataset_version: str = "fixture-0.1",
) -> tuple[Path, DatasetReferenceModel]:
    claims = load_evidence_claims(claims_path)
    sources = {source.source_id: source for source in load_evidence_sources(sources_path)}
    rows: list[dict[str, object]] = []
    for claim in claims:
        source = sources[claim.source_id]
        rows.append(
            {
                **claim.model_dump(mode="json"),
                "canonical_dataset_name": source.canonical_dataset_name,
                "dataset_card": source.dataset_card,
                "citation": source.citation,
                "provenance_manifest": source.provenance_manifest,
            }
        )
    content_hash = _combined_hash([claims_path, sources_path])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.intervention_effect_size_priors-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.intervention_effect_size_priors",
        version=dataset_version,
        content_hash=content_hash,
    )


def trace_claim(claim_id: str, claims_path: Path, sources_path: Path) -> dict[str, str]:
    claims = {claim.claim_id: claim for claim in load_evidence_claims(claims_path)}
    sources = {source.source_id: source for source in load_evidence_sources(sources_path)}
    claim = claims[claim_id]
    source = sources[claim.source_id]
    return {
        "claim_id": claim.claim_id,
        "source_id": source.source_id,
        "dataset_card": source.dataset_card,
        "provenance_manifest": source.provenance_manifest,
    }
