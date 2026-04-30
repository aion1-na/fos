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
    dataset_reference: DatasetReferenceModel
    dataset_card: str = Field(min_length=1)
    provenance_manifest: str = Field(min_length=1)
    citation: str = Field(min_length=1)
    license_ref: str = Field(min_length=1)
    quality_profile_ref: str = Field(min_length=1)


class ConfidenceInterval(BaseModel):
    model_config = ConfigDict(frozen=True)

    low: float
    high: float
    level: float = Field(gt=0, le=1)


class EvidenceClaim(BaseModel):
    model_config = ConfigDict(frozen=True)

    claim_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    transition_model_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    target_population: str = Field(min_length=1)
    treatment: str = Field(min_length=1)
    comparator: str = Field(min_length=1)
    outcome_domain: str = Field(min_length=1)
    effect_size: float
    effect_size_metric: str = Field(min_length=1)
    uncertainty: float = Field(ge=0)
    confidence_interval: ConfidenceInterval
    risk_of_bias: Literal["low", "medium", "high"]
    transportability: Literal["low", "medium", "high"]
    review_status: Literal["draft", "advisor_reviewed", "rejected", "superseded"]
    confidence_label: Literal["draft", "advisor_reviewed", "rejected", "superseded"]
    citation: str = Field(min_length=1)
    dataset_reference: DatasetReferenceModel
    provenance_link: str = Field(min_length=1)
    curator_notes: str = Field(min_length=1)

    @property
    def estimate(self) -> float:
        return self.effect_size

    @property
    def population(self) -> str:
        return self.target_population

    @property
    def outcome(self) -> str:
        return self.outcome_domain


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
                "estimate": claim.effect_size,
                "population": claim.target_population,
                "outcome": claim.outcome_domain,
                "canonical_dataset_name": source.canonical_dataset_name,
                "dataset_card": source.dataset_card,
                "source_citation": source.citation,
                "provenance_manifest": source.provenance_manifest,
            }
        )
    content_hash = _combined_hash([claims_path, sources_path])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"features.intervention_effect_size_priors_v1-{content_hash}.parquet"
    pq.write_table(pa.Table.from_pylist(rows), output_path)
    return output_path, DatasetReferenceModel(
        canonical_dataset_name="features.intervention_effect_size_priors_v1",
        version=dataset_version,
        content_hash=content_hash,
    )


def query_intervention_effect_size_priors(
    claims_path: Path,
    *,
    transition_model_id: str | None = None,
    scenario_id: str | None = None,
    review_status: Literal["draft", "advisor_reviewed", "rejected", "superseded"] | None = None,
) -> list[EvidenceClaim]:
    claims = load_evidence_claims(claims_path)
    return [
        claim
        for claim in claims
        if (transition_model_id is None or claim.transition_model_id == transition_model_id)
        and (scenario_id is None or claim.scenario_id == scenario_id)
        and (review_status is None or claim.review_status == review_status)
    ]


def priors_for_transition_model(
    transition_model_id: str,
    claims_path: Path,
) -> list[EvidenceClaim]:
    return query_intervention_effect_size_priors(
        claims_path,
        transition_model_id=transition_model_id,
    )


def priors_for_research_brief(
    scenario_id: str,
    claims_path: Path,
) -> list[dict[str, object]]:
    return [
        {
            "claim_id": claim.claim_id,
            "scenario_id": claim.scenario_id,
            "transition_model_id": claim.transition_model_id,
            "target_population": claim.target_population,
            "treatment": claim.treatment,
            "comparator": claim.comparator,
            "outcome_domain": claim.outcome_domain,
            "effect_size": claim.effect_size,
            "uncertainty": claim.uncertainty,
            "risk_of_bias": claim.risk_of_bias,
            "transportability": claim.transportability,
            "review_status": claim.review_status,
            "citation": claim.citation,
            "dataset_reference": claim.dataset_reference.model_dump(mode="json"),
        }
        for claim in query_intervention_effect_size_priors(
            claims_path,
            scenario_id=scenario_id,
        )
        if claim.review_status in {"draft", "advisor_reviewed"}
    ]


def trace_claim(claim_id: str, claims_path: Path, sources_path: Path) -> dict[str, object]:
    claims = {claim.claim_id: claim for claim in load_evidence_claims(claims_path)}
    sources = {source.source_id: source for source in load_evidence_sources(sources_path)}
    claim = claims[claim_id]
    source = sources[claim.source_id]
    return {
        "claim_id": claim.claim_id,
        "source_id": source.source_id,
        "dataset_card": source.dataset_card,
        "provenance_manifest": source.provenance_manifest,
        "dataset_reference": source.dataset_reference.model_dump(mode="json"),
    }
