from __future__ import annotations

from fw_contracts import CONTRACTS_VERSION, DomainPack, SpawnSpec
from fos_pack_toy_sir import (
    VACCINATION_INTERVENTION,
    apply_infection,
    apply_recovery,
    apply_vaccination,
    build_pack,
    run_validation,
    spawn_population,
)


def test_toy_sir_pack_exports_complete_domain_pack() -> None:
    pack = build_pack()

    assert isinstance(pack, DomainPack)
    assert pack.id == "toy-sir"
    assert pack.version == "0.1.0"
    assert pack.contracts_version == CONTRACTS_VERSION
    assert pack.state_schema["required"] == ["status", "days_since_infection", "age"]
    assert {model.id for model in pack.transition_models} == {"infection", "recovery"}
    assert pack.validation_suites[0].id == "sir-curve-mse"
    assert pack.render_hints.encodings["color_ramp"]["S"] == "#2f80ed"
    assert pack.render_hints.encodings["glyphs"]["I"] == "diamond"


def test_toy_sir_uses_spawnspec_and_runs_transitions() -> None:
    spec = SpawnSpec(
        population_id="e2e",
        count=1000,
        state_seed={"initial_infected": 10, "adult_share": 0.8},
    )

    agents = spawn_population(spec)
    assert len(agents) == spec.count
    assert sum(agent.state.status == "I" for agent in agents) == 10

    infected = apply_infection(agents)
    assert sum(agent.state.status == "I" for agent in infected) > 10

    recovered = apply_recovery(infected, recovery_days=1)
    assert all(agent.state.status != "I" for agent in recovered)

    vaccinated = apply_vaccination(agents, VACCINATION_INTERVENTION)
    adult_susceptible = [
        agent for agent in agents if agent.state.age >= 18 and agent.state.status == "S"
    ]
    adult_recovered = [
        agent for agent in vaccinated if agent.state.age >= 18 and agent.state.status == "R"
    ]
    assert len(adult_recovered) == len(adult_susceptible)


def test_toy_sir_validation_compares_curve_to_analytical_solution() -> None:
    result = run_validation()

    assert result["passed"] is True
    assert result["mse"] < result["threshold"]
    assert result["threshold"] == 0.05
