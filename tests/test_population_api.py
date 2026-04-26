from __future__ import annotations

from fos_api.main import (
    CohortFilter,
    CohortRequest,
    SpawnSpecRequest,
    create_cohort,
    create_population,
    get_agent,
    get_population_composition,
    list_cohorts,
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
