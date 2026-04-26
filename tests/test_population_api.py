from __future__ import annotations

from fos_api.main import (
    CohortFilter,
    CohortRequest,
    ProposedEditRequest,
    RunSpecRequest,
    SpawnSpecRequest,
    create_cohort,
    create_population,
    dry_run_scenario,
    get_agent,
    get_population_composition,
    invalidation_preview,
    list_cohorts,
    _stream_frames,
)


def test_population_endpoints_and_stable_cohort_ids() -> None:
    created = create_population(
        SpawnSpecRequest(population_id="api-population", count=5000, pack_id="flourishing", seed=7)
    )
    assert created["count"] == 5000

    composition = get_population_composition("api-population")
    assert composition["composition"]["attributes"][0]["status"] == "green"

    cohort_payload = CohortRequest(
        population_id="api-population",
        filters=[
            CohortFilter(
                population_id="api-population",
                field="income_percentile",
                operator=">=",
                value=0.5,
            )
        ],
    )
    first = create_cohort(cohort_payload)
    second = create_cohort(cohort_payload)
    assert first["id"] == second["id"]
    assert first["target_population"] == "api-population"

    agent_id = first["agent_ids"][0]
    agent = get_agent("api-population", str(agent_id))
    assert agent["id"] == agent_id

    cohorts = list_cohorts()
    assert first["id"] in {cohort["id"] for cohort in cohorts["cohorts"]}


def test_dry_run_invalidation_preview_and_stream_resume_frames() -> None:
    draft = dry_run_scenario(
        "scenario-default",
        RunSpecRequest(
            seeds=5,
            horizon_months=12,
            agent_count=500,
            runtime_tier="draft",
            evidence_mode="fixture-only",
            validation_gates=False,
            draft=True,
        ),
    )
    assert draft["valid"] is True
    assert draft["artifact_count"] == 2

    invalid = dry_run_scenario(
        "scenario-default",
        RunSpecRequest(
            seeds=5,
            horizon_months=12,
            agent_count=5000,
            runtime_tier="draft",
            evidence_mode="fixture-only",
            validation_gates=False,
            draft=True,
        ),
    )
    assert invalid["valid"] is False
    assert "draft runs must use 500 agents" in invalid["errors"]

    preview = invalidation_preview(
        "scenario-default",
        ProposedEditRequest(field="branch", value="paid-leave"),
    )
    artifacts = preview["invalidated_artifacts"]
    assert [artifact["stage"] for artifact in artifacts] == [
        "Population",
        "Execute",
        "Validate",
        "Brief",
    ]
    assert all(artifact["regenerationCost"] for artifact in artifacts)

    frames = _stream_frames("run_standard_001")
    assert frames[0]["type"] == "agent_update_count"
    assert frames[1]["type"] == "event_log_entry"
    assert frames[2]["type"] == "kpi_tick"
    assert frames[5:][0]["offset"] == 5
