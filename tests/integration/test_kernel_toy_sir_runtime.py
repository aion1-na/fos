from __future__ import annotations

import time
from pathlib import Path

from fos_pack_toy_sir import build_pack, spawn_population_state
from fw_contracts import Population, Scenario, SpawnSpec
from fw_kernel.artifact import load_artifact
from fw_kernel.runtime import run_simulation


def _toy_inputs(tmp_path: Path, ticks: int = 100) -> tuple[Scenario, Population, object]:
    spec = SpawnSpec(
        population_id="runtime-population",
        count=1000,
        state_seed={"initial_infected": 10, "adult_share": 0.8},
    )
    scenario = Scenario(
        id="runtime-scenario",
        domain_pack_id="toy-sir",
        name="Runtime scenario",
        parameters={
            "seed": 123,
            "ticks": ticks,
            "beta": 0.28,
            "recovery_days": 10,
            "artifact_dir": str(tmp_path / "artifact"),
            "allow_legacy_vectorized_transitions": True,
        },
    )
    population = Population(
        id=spec.population_id,
        scenario_id=scenario.id,
        size=spec.count,
        agent_ids=[f"{spec.population_id}-{index}" for index in range(spec.count)],
        metadata={"state": spawn_population_state(spec)},
    )
    return scenario, population, build_pack()


def test_kernel_runs_toy_sir_end_to_end_and_reloads_artifact(tmp_path: Path) -> None:
    scenario, population, pack = _toy_inputs(tmp_path)
    first = run_simulation(scenario, population, pack)
    first_artifact = load_artifact(tmp_path / "artifact")

    second_dir = tmp_path / "second-artifact"
    second_scenario = scenario.model_copy(
        update={"parameters": {**scenario.parameters, "artifact_dir": str(second_dir)}}
    )
    second = run_simulation(second_scenario, population, pack)
    second_artifact = load_artifact(second_dir)

    assert first.outputs["tick_hash_sequence"] == second.outputs["tick_hash_sequence"]
    assert first.outputs["kpis"] == second.outputs["kpis"]
    assert first_artifact["ticks_bytes"] == second_artifact["ticks_bytes"]
    assert first_artifact["kpis_bytes"] == second_artifact["kpis_bytes"]


def test_runtime_perf_budget_for_toy_sir(tmp_path: Path) -> None:
    scenario, population, pack = _toy_inputs(tmp_path)
    scenario = scenario.model_copy(
        update={
            "parameters": {
                key: value
                for key, value in scenario.parameters.items()
                if key != "artifact_dir"
            }
        }
    )

    started = time.perf_counter()
    run = run_simulation(scenario, population, pack)
    elapsed = time.perf_counter() - started

    assert run.status == "succeeded"
    assert len(run.outputs["tick_hash_sequence"]) == 100
    assert elapsed < 2.0
