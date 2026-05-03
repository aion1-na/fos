from __future__ import annotations

from pathlib import Path
import json

from fos_data_pipelines.evidence_graph.claims import load_evidence_claims

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = (
    ROOT
    / "packages"
    / "data-pipelines"
    / "fixtures"
    / "evidence_graph"
    / "evidence_claims_fixture_only.json"
)


def test_every_claim_has_auditable_transportability_and_bias_labels() -> None:
    for claim in load_evidence_claims(CLAIMS):
        assert claim.transportability in {"low", "medium", "high"}
        assert claim.risk_of_bias in {"low", "medium", "high"}
        assert claim.confidence_interval.low <= claim.effect_size <= claim.confidence_interval.high
        assert claim.dataset_reference.version == "request-status-v0.1"


def test_family_support_null_priors_are_not_advisor_ready_effects() -> None:
    family_claims = [
        claim for claim in load_evidence_claims(CLAIMS) if claim.scenario_id == "family_support"
    ]

    assert family_claims
    assert all(claim.review_status == "draft" for claim in family_claims)
    assert all(claim.effect_size == 0.0 for claim in family_claims)
    assert all("fixture-only null prior" in claim.curator_notes.lower() for claim in family_claims)


def test_contract_schema_requires_rs07_effect_size_fields() -> None:
    schema = json.loads(
        (
            ROOT / "packages" / "contracts" / "schemas" / "v0.1" / "EvidenceClaim.schema.json"
        ).read_text(encoding="utf-8")
    )

    assert {
        "source_id",
        "target_population",
        "treatment",
        "comparator",
        "outcome_domain",
        "effect_size",
        "uncertainty",
        "risk_of_bias",
        "transportability",
        "citation",
        "dataset_reference",
    } <= set(schema["required"])
