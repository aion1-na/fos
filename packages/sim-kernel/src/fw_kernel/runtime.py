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
from fw_kernel.evidence_engine import (
    EvidenceBoundedTransitionEngine,
    TransitionInputBundle,
    compile_scenario_target_trials,
    run_statistical_baseline,
)
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
from fw_kernel.types import RuntimeContext, TickRecord, TransitionPatch

DEFAULT_TICKS = 100
INTERVENTION_PRIORS_FEATURE = "features.intervention_effect_size_priors_v1"


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


def _unique_dataset_references(references: list[Any]) -> list[Any]:
    seen: set[tuple[str, str, str]] = set()
    unique: list[Any] = []
    for reference in references:
        key = (
            reference.canonical_dataset_name,
            reference.version,
            reference.content_hash,
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(reference)
    return unique


def _has_dataset_reference(references: list[Any], canonical_dataset_name: str) -> bool:
    return any(
        reference.canonical_dataset_name == canonical_dataset_name
        for reference in references
    )


def _has_dataset_reference_tuple(references: list[Any], reference: Any) -> bool:
    key = (
        reference.canonical_dataset_name,
        reference.version,
        reference.content_hash,
    )
    return any(
        (
            candidate.canonical_dataset_name,
            candidate.version,
            candidate.content_hash,
        )
        == key
        for candidate in references
    )


def _evidence_transition_patch(
    *,
    snapshot: Any,
    bounded_results: list[dict[str, Any]],
    apply_state_effects: bool,
) -> TransitionPatch:
    fields: dict[str, np.ndarray] = {}
    masks: dict[str, np.ndarray] = {}
    kpis: dict[str, float] = {}
    for result in bounded_results:
        domain = result["outcome_domain"]
        expected_effect = float(result["expected_effect"])
        kpis[f"evidence_bounded.{domain}.expected_effect"] = expected_effect
        if not apply_state_effects:
            continue
        if domain not in snapshot.fields:
            continue
        current = snapshot.fields[domain]
        if not np.issubdtype(current.dtype, np.number):
            continue
        fields[domain] = current + expected_effect
        masks[domain] = np.ones(snapshot.size, dtype=bool)
    return TransitionPatch(
        transition_id="evidence_bounded_transition_engine",
        mode="replace",
        fields=fields,
        masks=masks,
        kpis=kpis,
    )


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
    if parameters.get("require_dataset_references") and not dataset_references:
        raise ValueError("simulation-facing outputs require dataset_references")
    target_trial_specs = []
    if "target_trials" in parameters:
        target_trial_specs = compile_scenario_target_trials(scenario)
        dataset_references = _unique_dataset_references(
            [
                *dataset_references,
                *[
                    reference
                    for spec in target_trial_specs
                    for reference in (
                        spec.evidence_prior.dataset_reference,
                        spec.evidence_prior.feature_dataset_reference,
                    )
                    if reference is not None
                ],
            ]
        )
        for spec in target_trial_specs:
            feature_reference = spec.evidence_prior.feature_dataset_reference
            if feature_reference is not None:
                if not _has_dataset_reference_tuple(dataset_references, feature_reference):
                    raise ValueError(
                        "evidence-bounded transitions require exact dataset_reference for "
                        f"{INTERVENTION_PRIORS_FEATURE}"
                    )
            elif not _has_dataset_reference(dataset_references, INTERVENTION_PRIORS_FEATURE):
                raise ValueError(
                    "evidence-bounded transitions require dataset_reference for "
                    f"{INTERVENTION_PRIORS_FEATURE}"
                )
    elif parameters.get("require_evidence_bounded_transitions"):
        raise ValueError("evidence-bounded transition engine requires target_trials")
    ticks = int(parameters.get("ticks", DEFAULT_TICKS))
    seed = int(parameters.get("seed", 0))
    enabled_transitions = parameters.get("transitions")
    if enabled_transitions is not None and not isinstance(enabled_transitions, list):
        raise TypeError("scenario.parameters['transitions'] must be a list")
    allow_vectorized_with_evidence = bool(parameters.get("allow_vectorized_measurement_transitions"))
    allow_legacy_vectorized_transitions = bool(parameters.get("allow_legacy_vectorized_transitions"))
    if pack.transition_models and not target_trial_specs and not allow_legacy_vectorized_transitions:
        raise ValueError("vectorized transitions require target_trials or explicit legacy opt-in")

    rng = np.random.default_rng(seed)
    state = state_from_population(population)
    records: list[TickRecord] = []
    bounded_results: list[dict[str, Any]] = []
    if target_trial_specs:
        transition_engine = EvidenceBoundedTransitionEngine()
        bundle_payload = parameters.get("transition_input_bundle", {})
        if not isinstance(bundle_payload, dict):
            raise TypeError("scenario.parameters['transition_input_bundle'] must be an object")
        transition_bundle = TransitionInputBundle.model_validate(bundle_payload)
        bounded_results = [
            transition_engine.run(
                spec,
                seed=seed + index,
                bundle=transition_bundle,
            ).model_dump(mode="json")
            for index, spec in enumerate(target_trial_specs)
        ]

    for tick in range(ticks):
        snapshot = take_snapshot(state)
        if target_trial_specs and not allow_vectorized_with_evidence:
            applicable = []
        else:
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
        if bounded_results:
            patches.append(
                _evidence_transition_patch(
                    snapshot=snapshot,
                    bounded_results=bounded_results,
                    apply_state_effects=tick == 0,
                )
            )
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
    if target_trial_specs:
        outputs["evidence_bounded_transition_results"] = bounded_results
        outputs["statistical_baseline"] = run_statistical_baseline(
            manifest.model_dump(mode="json"),
            target_trial_specs,
        )
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
