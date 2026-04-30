from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from fw_contracts import DomainPack, Population, Scenario, SimulationRun

from fw_kernel.applicability import applicable_transitions
from fw_kernel.artifact import write_artifact
from fw_kernel.commit import commit_patch
from fw_kernel.compute import compute_transition
from fw_kernel.network import propagate_once
from fw_kernel.order import deterministic_order
from fw_kernel.provenance import (
    collect_dataset_references,
    reject_unversioned_dataset_reads,
    run_data_manifest,
    tick_hash,
)
from fw_kernel.resolve import resolve_composition
from fw_kernel.snapshot import take_snapshot
from fw_kernel.state import state_from_population
from fw_kernel.types import RuntimeContext, TickRecord

DEFAULT_TICKS = 100


def _stable_run_id(scenario: Scenario, population: Population, pack: DomainPack) -> str:
    payload = {
        "scenario": scenario.model_dump(mode="json"),
        "population": population.model_dump(mode="json"),
        "pack": pack.model_dump(mode="json"),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:24]


def _parameter_dict(scenario: Scenario) -> dict[str, Any]:
    return dict(scenario.parameters)


def run_simulation(
    scenario: Scenario,
    population: Population,
    pack: DomainPack,
) -> SimulationRun:
    if scenario.domain_pack_id != pack.id:
        raise ValueError("scenario domain_pack_id must match pack id")
    if population.scenario_id != scenario.id:
        raise ValueError("population scenario_id must match scenario id")

    parameters = _parameter_dict(scenario)
    population_metadata = dict(population.metadata)
    pack_metadata = {"dataset_references": pack.model_dump(mode="json").get("dataset_references", [])}
    reject_unversioned_dataset_reads(parameters, population_metadata, pack_metadata)
    dataset_references = collect_dataset_references(parameters, population_metadata, pack_metadata)
    ticks = int(parameters.get("ticks", DEFAULT_TICKS))
    seed = int(parameters.get("seed", 0))
    enabled_transitions = parameters.get("transitions")
    if enabled_transitions is not None and not isinstance(enabled_transitions, list):
        raise TypeError("scenario.parameters['transitions'] must be a list")

    rng = np.random.default_rng(seed)
    state = state_from_population(population)
    records: list[TickRecord] = []

    for tick in range(ticks):
        snapshot = take_snapshot(state)
        applicable = applicable_transitions(pack.transition_models, enabled_transitions)
        ordered = deterministic_order(applicable)
        context = RuntimeContext(
            run_seed=seed,
            tick=tick,
            scenario_parameters=parameters,
        )
        patches = [
            compute_transition(transition, snapshot, rng, context)
            for transition in ordered
        ]
        resolved = resolve_composition(patches)
        propagated = propagate_once(snapshot, resolved)
        state = commit_patch(state, propagated)
        hash_value = tick_hash(tick, state, propagated.kpis)
        records.append(
            TickRecord(
                tick=tick,
                state=state.copy(),
                kpis=propagated.kpis,
                tick_hash=hash_value,
            )
        )

    run_id = _stable_run_id(scenario, population, pack)
    manifest = run_data_manifest(
        run_id=run_id,
        scenario_id=scenario.id,
        population_id=population.id,
        dataset_references=dataset_references,
    )
    branch_manifests = [
        run_data_manifest(
            run_id=run_id,
            scenario_id=scenario.id,
            population_id=population.id,
            dataset_references=dataset_references,
            branch_id=branch.id,
            parent_branch_id=branch.parent_id,
        )
        for branch in scenario.branches
    ]
    outputs: dict[str, Any] = {
        "tick_hash_sequence": [record.tick_hash for record in records],
        "kpis": [record.kpis for record in records],
        "run_data_manifest": manifest.model_dump(mode="json"),
        "branch_data_manifests": [
            branch_manifest.model_dump(mode="json")
            for branch_manifest in branch_manifests
        ],
    }
    output_dir = parameters.get("artifact_dir")
    if output_dir is not None:
        artifact = write_artifact(
            Path(str(output_dir)),
            run_id=run_id,
            scenario_id=scenario.id,
            population_id=population.id,
            records=records,
            run_data_manifest=manifest,
        )
        outputs["artifact_manifest"] = artifact.manifest
        outputs["artifact_dir"] = str(Path(str(output_dir)))

    return SimulationRun(
        id=run_id,
        scenario_id=scenario.id,
        population_id=population.id,
        status="succeeded",
        outputs=outputs,
    )
