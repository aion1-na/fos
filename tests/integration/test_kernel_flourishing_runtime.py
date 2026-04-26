from __future__ import annotations

from pathlib import Path

from fos_pack_flourishing import build_pack, build_population
from fw_contracts import Scenario, SpawnSpec
from fw_kernel.artifact import load_artifact
from fw_kernel.runtime import run_simulation


def _flourishing_inputs(tmp_path: Path) -> tuple[Scenario, object, object]:
    scenario = Scenario(
        id="flourishing-runtime-scenario",
        domain_pack_id="flourishing",
        name="Flourishing runtime scenario",
        parameters={
            "seed": 321,
            "ticks": 6,
            "paid_leave_time_boost": 0.02,
            "income_policy_boost": 0.01,
            "mentoring_relationship_boost": 0.01,
            "mentoring_purpose_boost": 0.01,
            "artifact_dir": str(tmp_path / "artifact"),
        },
    )
    spec = SpawnSpec(
        population_id="flourishing-runtime-population",
        count=240,
        state_seed={"seed": 88},
    )
    return scenario, build_population(scenario, spec), build_pack()


def test_kernel_runs_flourishing_end_to_end_without_kernel_changes(tmp_path: Path) -> None:
    scenario, population, pack = _flourishing_inputs(tmp_path)

    first = run_simulation(scenario, population, pack)
    first_artifact = load_artifact(tmp_path / "artifact")
    second_dir = tmp_path / "second-artifact"
    second_scenario = scenario.model_copy(
        update={"parameters": {**scenario.parameters, "artifact_dir": str(second_dir)}}
    )
    second = run_simulation(second_scenario, population, pack)
    second_artifact = load_artifact(second_dir)

    assert first.status == "succeeded"
    assert len(first.outputs["tick_hash_sequence"]) == 6
    assert first.outputs["tick_hash_sequence"] == second.outputs["tick_hash_sequence"]
    assert first.outputs["kpis"] == second.outputs["kpis"]
    assert first_artifact["ticks_bytes"] == second_artifact["ticks_bytes"]
    assert first_artifact["kpis_bytes"] == second_artifact["kpis_bytes"]
