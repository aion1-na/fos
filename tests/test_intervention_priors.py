from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.evidence_graph.claims import (
    build_intervention_effect_size_priors,
    load_evidence_claims,
    load_evidence_sources,
    priors_for_concordia_scene_compiler,
    priors_for_research_brief,
    priors_for_transition_model,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "evidence_graph"
CLAIMS = FIXTURES / "evidence_claims_fixture_only.json"
SOURCES = FIXTURES / "intervention_sources_fixture_only.json"


def test_intervention_library_has_required_review_depth_and_family_support() -> None:
    claims = load_evidence_claims(CLAIMS)
    scenarios = {claim.scenario_id for claim in claims}

    assert len([claim for claim in claims if claim.review_status == "draft"]) >= 75
    assert len([claim for claim in claims if claim.review_status == "advisor_reviewed"]) >= 25
    assert {
        "job_training_retraining",
        "registered_apprenticeship",
        "mentoring",
        "financial_stabilization_cash_transfer",
        "mental_health_access",
        "community_belonging_social_prescribing",
        "education_support",
        "healthcare_decoupling",
        "eitc",
        "moving_to_opportunity",
        "job_corps",
        "family_support",
    } <= scenarios


def test_intervention_priors_feature_table_is_content_addressed(tmp_path: Path) -> None:
    output_path, reference = build_intervention_effect_size_priors(CLAIMS, SOURCES, tmp_path)
    rows = pq.read_table(output_path).to_pylist()

    assert reference.canonical_dataset_name == "features.intervention_effect_size_priors_v1"
    assert len(reference.content_hash) == 64
    assert output_path.name.endswith(f"{reference.content_hash}.parquet")
    assert rows
    assert all(row["dataset_reference"] for row in rows)
    assert all(
        row["dataset_reference"]["canonical_dataset_name"]
        == "features.intervention_effect_size_priors_v1"
        for row in rows
    )
    assert all(row["source_dataset_reference"] for row in rows)


def test_intervention_priors_query_all_consumers_without_external_tools() -> None:
    transition = priors_for_transition_model("employment_transition", CLAIMS)
    brief = priors_for_research_brief("family_support", CLAIMS)
    concordia = priors_for_concordia_scene_compiler("family_support", CLAIMS)

    assert transition
    assert brief
    assert concordia
    assert all(row["may_set_causal_effect_size"] is False for row in concordia)
    assert all(row["qualitative_scene_context_only"] is True for row in concordia)
    assert all("effect_size" not in row for row in concordia)
    assert all("uncertainty" not in row for row in concordia)


def test_by_request_literature_sources_are_request_status_not_fake_microdata() -> None:
    sources = load_evidence_sources(SOURCES)

    assert sources
    assert all(source.access_status == "request_status_stub" for source in sources)
    assert all(source.dataset_reference.version == "request-status-v0.1" for source in sources)
    assert all("microdata" not in source.dataset_card for source in sources)
    assert all((ROOT / source.dataset_card).exists() for source in sources)
    assert all((ROOT / source.quality_profile_ref).exists() for source in sources)
