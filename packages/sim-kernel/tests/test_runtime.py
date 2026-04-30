from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from fw_contracts import BranchSpec, DomainPack, Population, Scenario, TransitionModel
from fw_kernel.artifact import load_artifact
from fw_kernel.resolve import resolve_composition
from fw_kernel.runtime import run_simulation
from fw_kernel.types import TransitionPatch


def _inputs(tmp_path: Path, ticks: int = 3) -> tuple[Scenario, Population, DomainPack]:
    scenario = Scenario(
        id="runtime-scenario",
        domain_pack_id="generic-pack",
        name="Runtime scenario",
        parameters={
            "seed": 123,
            "ticks": ticks,
            "amount": 2,
            "artifact_dir": str(tmp_path / "artifact"),
        },
    )
    population = Population(
        id="runtime-population",
        scenario_id=scenario.id,
        size=4,
        agent_ids=["a", "b", "c", "d"],
        metadata={"state": {"value": [0, 1, 2, 3]}},
    )
    pack = DomainPack(
        id="generic-pack",
        name="Generic Pack",
        version="0.1.0",
        state_schema={"type": "object"},
        transition_models=[
            TransitionModel(
                id="increment",
                version="0.1.0",
                entrypoint="fw_kernel.testing_transitions.increment_value",
            )
        ],
    )
    return scenario, population, pack


def test_runtime_artifact_reloads_identically(tmp_path: Path) -> None:
    scenario, population, pack = _inputs(tmp_path)
    first = run_simulation(scenario, population, pack)
    first_artifact = load_artifact(tmp_path / "artifact")

    second_dir = tmp_path / "second-artifact"
    second_scenario = scenario.model_copy(
        update={"parameters": {**scenario.parameters, "artifact_dir": str(second_dir)}}
    )
    second = run_simulation(second_scenario, population, pack)
    second_artifact = load_artifact(second_dir)

    assert first.status == "succeeded"
    assert first.outputs["tick_hash_sequence"] == second.outputs["tick_hash_sequence"]
    assert first.outputs["kpis"] == second.outputs["kpis"]
    assert first_artifact["ticks_bytes"] == second_artifact["ticks_bytes"]
    assert first_artifact["kpis_bytes"] == second_artifact["kpis_bytes"]


def test_runtime_emits_run_data_manifest_for_all_simulation_components(tmp_path: Path) -> None:
    scenario, population, pack = _inputs(tmp_path)
    reference = {
        "canonical_dataset_name": "features.community_context",
        "version": "fixture-0.1",
        "content_hash": "a" * 64,
    }
    scenario = scenario.model_copy(
        update={
            "branches": [BranchSpec(id="treatment", label="Treatment")],
            "parameters": {
                **scenario.parameters,
                "dataset_references": [reference],
            },
        }
    )

    run = run_simulation(scenario, population, pack)
    manifest = run.outputs["run_data_manifest"]
    artifact = load_artifact(tmp_path / "artifact")

    assert manifest["dataset_references"] == [reference]
    assert set(manifest["touched_components"]) == {
        "population_synthesis",
        "transition_models",
        "validation",
        "adapter_artifacts",
    }
    assert run.outputs["branch_data_manifests"][0]["branch_id"] == "treatment"
    assert artifact["manifest"]["run_data_manifest"]["dataset_references"] == [reference]


def test_runtime_rejects_raw_dataset_path_reads(tmp_path: Path) -> None:
    scenario, population, pack = _inputs(tmp_path)
    scenario = scenario.model_copy(
        update={"parameters": {**scenario.parameters, "reference_path": "fixtures/raw.parquet"}}
    )

    with pytest.raises(ValueError, match="unversioned dataset read"):
        run_simulation(scenario, population, pack)


def test_determinism_across_processes(tmp_path: Path) -> None:
    script = f"""
import json
from pathlib import Path
from fw_contracts import DomainPack, Population, Scenario, TransitionModel
from fw_kernel.runtime import run_simulation

tmp_path = Path({str(tmp_path)!r})
scenario = Scenario(
    id="runtime-scenario",
    domain_pack_id="generic-pack",
    name="Runtime scenario",
    parameters={{"seed": 123, "ticks": 3, "amount": 2}},
)
population = Population(
    id="runtime-population",
    scenario_id=scenario.id,
    size=4,
    agent_ids=["a", "b", "c", "d"],
    metadata={{"state": {{"value": [0, 1, 2, 3]}}}},
)
pack = DomainPack(
    id="generic-pack",
    name="Generic Pack",
    version="0.1.0",
    state_schema={{"type": "object"}},
    transition_models=[
        TransitionModel(
            id="increment",
            version="0.1.0",
            entrypoint="fw_kernel.testing_transitions.increment_value",
        )
    ],
)
run = run_simulation(scenario, population, pack)
print(json.dumps({{
    "tick_hash_sequence": run.outputs["tick_hash_sequence"],
    "kpis": run.outputs["kpis"],
}}, sort_keys=True))
"""
    outputs = [
        subprocess.check_output([sys.executable, "-c", script], text=True)
        for _ in range(2)
    ]
    assert json.loads(outputs[0]) == json.loads(outputs[1])


def test_composition_resolver_rejects_conflicting_replace() -> None:
    first = TransitionPatch(
        transition_id="first",
        mode="replace",
        fields={"x": np.asarray([1, 0])},
        masks={"x": np.asarray([True, False])},
    )
    second = TransitionPatch(
        transition_id="second",
        mode="replace",
        fields={"x": np.asarray([2, 0])},
        masks={"x": np.asarray([True, False])},
    )

    with pytest.raises(ValueError, match="conflicting replace"):
        resolve_composition([first, second])


def test_network_propagation_is_exactly_one_pass(tmp_path: Path) -> None:
    scenario, population, pack = _inputs(tmp_path, ticks=1)
    run = run_simulation(scenario, population, pack)

    assert len(run.outputs["tick_hash_sequence"]) == 1
