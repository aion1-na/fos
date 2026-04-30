from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.evidence_graph.claims import (
    build_intervention_effect_size_priors,
    load_evidence_claims,
    load_evidence_sources,
    priors_for_research_brief,
    priors_for_transition_model,
    trace_claim,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "evidence_graph"
CLAIMS = FIXTURES / "evidence_claims.json"
SOURCES = FIXTURES / "intervention_sources.json"


def test_every_effect_size_has_required_claim_fields() -> None:
    claims = load_evidence_claims(CLAIMS)

    assert len([claim for claim in claims if claim.review_status == "draft"]) >= 75
    assert len([claim for claim in claims if claim.review_status == "advisor_reviewed"]) >= 25
    for claim in claims:
        assert claim.source_id
        assert isinstance(claim.estimate, float)
        assert isinstance(claim.effect_size, float)
        assert claim.uncertainty >= 0
        assert claim.target_population
        assert claim.treatment
        assert claim.comparator
        assert claim.outcome_domain
        assert claim.confidence_label in {"draft", "advisor_reviewed", "rejected", "superseded"}
        assert claim.risk_of_bias in {"low", "medium", "high"}
        assert claim.transportability in {"low", "medium", "high"}
        assert claim.citation
        assert claim.dataset_reference.canonical_dataset_name.startswith("intervention_literature.")
        assert claim.provenance_link


def test_by_request_sources_are_request_status_records() -> None:
    sources = load_evidence_sources(SOURCES)

    assert sources
    assert all(source.access_status == "request_status_stub" for source in sources)
    assert all(source.dataset_card.startswith("docs/data/datasets/") for source in sources)
    assert all(source.dataset_reference.version == "request-status-v0.1" for source in sources)


def test_advisor_reviewed_claims_are_distinguishable_from_draft_claims() -> None:
    claims = load_evidence_claims(CLAIMS)
    statuses = {claim.review_status for claim in claims}

    assert "advisor_reviewed" in statuses
    assert "draft" in statuses
    reviewed = [claim for claim in claims if claim.review_status == "advisor_reviewed"]
    assert all(claim.confidence_label == "advisor_reviewed" for claim in reviewed)


def test_intervention_effect_size_priors_emit_required_columns(tmp_path: Path) -> None:
    output_path, reference = build_intervention_effect_size_priors(CLAIMS, SOURCES, tmp_path)
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.intervention_effect_size_priors_v1"
    assert len(reference.content_hash) == 64
    for row in rows:
        for required in [
            "source_id",
            "effect_size",
            "uncertainty",
            "target_population",
            "treatment",
            "comparator",
            "outcome_domain",
            "outcome",
            "confidence_label",
            "provenance_link",
            "dataset_card",
            "provenance_manifest",
            "dataset_reference",
        ]:
            assert row[required] is not None
            assert row[required] != ""


def test_claim_trace_links_source_dataset_card_and_provenance_manifest() -> None:
    trace = trace_claim("claim_job_training_retraining_financial_security_v1", CLAIMS, SOURCES)

    assert trace["claim_id"] == "claim_job_training_retraining_financial_security_v1"
    assert trace["source_id"] == "src_job_training_request_status"
    assert trace["dataset_card"] == "docs/data/datasets/job-training-literature.md"
    assert trace["provenance_manifest"] == "request-status:job_training-literature"


def test_priors_are_queryable_by_transition_model_and_research_brief() -> None:
    transition_priors = priors_for_transition_model("employment_transition", CLAIMS)
    brief_priors = priors_for_research_brief("job_corps", CLAIMS)

    assert transition_priors
    assert all(claim.transition_model_id == "employment_transition" for claim in transition_priors)
    assert brief_priors
    assert all(row["scenario_id"] == "job_corps" for row in brief_priors)
    assert all(row["review_status"] in {"draft", "advisor_reviewed"} for row in brief_priors)


def test_evidence_graph_migration_initializes_age_and_tables() -> None:
    migration = (
        ROOT / "packages" / "data-service" / "migrations" / "002_evidence_graph.sql"
    ).read_text(encoding="utf-8")

    assert "CREATE EXTENSION IF NOT EXISTS age" in migration
    assert "SELECT create_graph('evidence_graph')" in migration
    assert "evidence_graph.claims" in migration
    assert "evidence_graph.citations" in migration
    assert "evidence_graph.causal_edges" in migration


def test_atlas_trace_view_contains_claim_source_card_and_provenance() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "evidence" / "page.tsx").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "apps" / "atlas" / "lib" / "evidence" / "claims.ts").read_text(
        encoding="utf-8"
    )

    assert "claim.sourceId" in page
    assert "claim.datasetCard" in page
    assert "claim.provenanceManifest" in page
    assert "advisor_reviewed" in source
    assert "draft" in source
    assert "superseded" in source
