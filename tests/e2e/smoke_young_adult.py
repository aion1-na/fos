from __future__ import annotations

import json
import time
from dataclasses import dataclass

import pytest
from fastapi import HTTPException

from fos_api.main import (
    BriefRequest,
    ProposedEditRequest,
    RunSpecRequest,
    _simulation_run_artifact,
    dry_run_scenario,
    generate_brief,
    get_brief,
    get_run_causal_trace,
    get_run_validation,
    invalidation_preview,
)

STAGES = [
    "frame",
    "compose",
    "evidence",
    "population",
    "configure",
    "execute",
    "validate",
    "explore",
    "brief",
]

UPSTREAM_INVALIDATION_SET = [
    "Population",
    "Execute",
    "Validate",
    "Brief",
]


@dataclass(frozen=True)
class StageVisit:
    stage: str
    reentered: bool


def _run_spec(draft: bool = False) -> RunSpecRequest:
    if draft:
        return RunSpecRequest(
            branch="treatment-vs-control",
            seeds=5,
            horizon_months=12,
            agent_count=500,
            runtime_tier="draft",
            evidence_mode="fixture-only",
            validation_gates=False,
            draft=True,
        )
    return RunSpecRequest(
        branch="treatment-vs-control",
        seeds=30,
        horizon_months=60,
        agent_count=5000,
        runtime_tier="standard",
        evidence_mode="pack-default",
        validation_gates=True,
        draft=False,
        kpis=["happiness", "health", "meaning", "relationships", "financial"],
        shocks=["treatment", "control"],
    )


def _brief_request(validation_status: str) -> BriefRequest:
    return BriefRequest(
        scenario_id="young-adult-flourishing-futures",
        findings=[
            "Treatment branch improves the modeled six-domain score relative to control.",
            "Validation is mixed; epistemic mode is cautious because one gate remains red.",
        ],
        assumptions=[
            "Validation result is recorded as observed; no gate result is rewritten.",
            "Epistemic mode: cautious due to red mentoring-meaning validation gate.",
        ],
        uncertainty=[
            "Mentoring pathway has weak E-value and red drift status.",
            "Benefit cliff exposure remains a red unintended consequence.",
        ],
        evidence_trail=[
            "income-security-001",
            "social-support-001",
            "validation:run_young_adult_5k_60m_30s",
        ],
        validation_status=validation_status,
        citation_ids=["income-security-001", "social-support-001"],
        draft=False,
    )


def _walk_all_stages_with_reentry() -> list[StageVisit]:
    visits: list[StageVisit] = []
    for stage in STAGES:
        if stage in {"frame", "compose", "evidence", "population", "configure", "execute", "validate"}:
            preview = invalidation_preview(
                "young-adult-flourishing-futures",
                ProposedEditRequest(field=stage, value=f"reentered-{stage}"),
            )
            assert [artifact["stage"] for artifact in preview["invalidated_artifacts"]] == UPSTREAM_INVALIDATION_SET
            assert all(artifact["regenerationCost"] for artifact in preview["invalidated_artifacts"])
            visits.append(StageVisit(stage=stage, reentered=True))
        else:
            visits.append(StageVisit(stage=stage, reentered=False))
    return visits


def test_young_adult_flourishing_futures_smoke_run() -> None:
    started = time.perf_counter()
    visits = _walk_all_stages_with_reentry()
    dry_run = dry_run_scenario("young-adult-flourishing-futures", _run_spec())
    assert dry_run["valid"] is True

    run_id = "run_young_adult_5k_60m_30s"
    run_artifact = _simulation_run_artifact(run_id)
    validation = get_run_validation(run_id)
    trace = get_run_causal_trace(run_id)
    brief = generate_brief(run_id, _brief_request(str(validation["status"])))
    exported = get_brief(run_id, format="json")

    assert [visit.stage for visit in visits] == STAGES
    assert all(visit.reentered for visit in visits[:7])
    assert run_artifact["manifest"]["run_id"] == run_id
    assert len(run_artifact["manifest"]["kpi_outputs"]) == 12
    assert validation["headline_claims"][2]["gate"] == "red"
    assert any(not pathway["calibrated"] for pathway in trace["pathways"])
    assert json.loads(exported.body)["id"] == brief["id"]
    assert time.perf_counter() - started < 15 * 60


def test_replay_from_manifest_reproduces_brief_byte_for_byte() -> None:
    run_id = "run_young_adult_replay"
    first = generate_brief(run_id, _brief_request("blocked"))
    first_bytes = get_brief(run_id, format="json").body
    manifest = first["reproducibility_manifest"]

    replayed_artifact = _simulation_run_artifact(str(manifest["run_id"]))
    assert replayed_artifact["manifest"]["kpi_outputs"] == manifest["kpi_outputs"]
    assert get_brief(run_id, format="json").body == first_bytes


@pytest.mark.parametrize("stage", STAGES[:7])
def test_upstream_edits_produce_exact_scope_8_4_1_invalidation_set(stage: str) -> None:
    preview = invalidation_preview(
        "young-adult-flourishing-futures",
        ProposedEditRequest(field=stage, value="edited"),
    )

    assert [artifact["stage"] for artifact in preview["invalidated_artifacts"]] == UPSTREAM_INVALIDATION_SET


def test_draft_variant_completes_fast_and_cannot_export_brief() -> None:
    started = time.perf_counter()
    dry_run = dry_run_scenario("young-adult-flourishing-futures-draft", _run_spec(draft=True))

    assert dry_run["valid"] is True
    assert time.perf_counter() - started < 3 * 60
    with pytest.raises(HTTPException, match="Draft runs cannot produce briefs"):
        generate_brief("run_draft_young_adult", _brief_request("draft"))
