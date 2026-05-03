from __future__ import annotations

from pathlib import Path

import pytest
from fw_contracts import DomainPack, Population, Scenario, TransitionModel
from fw_kernel import (
    EvidenceBoundedTransitionEngine,
    TransitionInputBundle,
    compile_scenario_target_trials,
    compile_target_trial_spec,
    run_statistical_baseline,
)
from fw_kernel.runtime import run_simulation

from target_trial_fixture_only import target_trial_payload_fixture_only

ROOT = Path(__file__).resolve().parents[1]
FEATURE_REFERENCE = {
    "canonical_dataset_name": "features.intervention_effect_size_priors_v1",
    "version": "fixture-0.1",
    "content_hash": "b" * 64,
}


def test_transition_kernel_separates_input_lanes_and_returns_required_outputs() -> None:
    engine = EvidenceBoundedTransitionEngine(posterior_draw_count=500)
    result = engine.run(
        spec=compile_target_trial_spec(target_trial_payload_fixture_only()),
        bundle=TransitionInputBundle(
            measurement_inputs={"exposure_measures": {"measure_a": 0.2, "measure_b": 0.4}},
            network_effects={"peer_support": 0.01},
            concordia_cognition_traces=[{"artifact_id": "concordia-scene", "summary": "qualitative"}],
            graph_visualization_artifacts=[{"artifact_id": "graph-layout", "layout": "force"}],
        ),
        seed=7,
    )

    assert engine.posterior_draw_count == 500
    assert result.separated_inputs["measurement"]["exposure_measures"]["measure_a"] == 0.2
    assert result.separated_inputs["concordia_cognition_traces"][0]["artifact_id"] == "concordia-scene"
    assert result.separated_inputs["graph_visualization_artifacts"][0]["artifact_id"] == "graph-layout"


def test_transition_kernel_result_contains_lineage_uncertainty_harm_and_heterogeneity() -> None:
    engine = EvidenceBoundedTransitionEngine(posterior_draw_count=500)
    result = engine.run(
        compile_target_trial_spec(target_trial_payload_fixture_only()),
        TransitionInputBundle(network_effects={"peer_support": 0.01}),
        seed=8,
    )

    assert "lower" in result.uncertainty_interval
    assert "upper" in result.uncertainty_interval
    assert 0 <= result.probability_of_harm <= 1
    assert result.subgroup_heterogeneity["status"] == "not_estimated"
    assert result.subgroup_heterogeneity["subgroup_estimates"] == {}
    assert result.data_lineage[0]["content_hash"] == "a" * 64
    assert result.separated_inputs["network_effects"] == {"peer_support": 0.01}


def test_statistical_baseline_runs_on_same_manifest() -> None:
    spec = compile_target_trial_spec(target_trial_payload_fixture_only())
    baseline = run_statistical_baseline(
        {
            "run_id": "run_fixture_only",
            "dataset_references": [
                spec.evidence_prior.dataset_reference.model_dump(mode="json"),
                FEATURE_REFERENCE,
            ],
        },
        [spec],
    )

    assert baseline["baseline_method"] == "mean_prior_effect"
    assert "uncertainty_interval" in baseline
    assert "probability_of_harm" in baseline
    assert "subgroup_heterogeneity" in baseline
    assert baseline["data_lineage"][0]["content_hash"] == "a" * 64


def test_runtime_wires_evidence_bounded_transition_results(tmp_path: Path) -> None:
    scenario = Scenario(
        id="job_training_retraining",
        domain_pack_id="generic-pack",
        name="Runtime target trial",
        parameters={
            "seed": 3,
            "ticks": 1,
            "amount": 1,
            "artifact_dir": str(tmp_path / "artifact"),
            "dataset_references": [FEATURE_REFERENCE],
            "target_trials": [target_trial_payload_fixture_only()],
            "transition_input_bundle": {
                "measurement_inputs": {"exposure_measures": {"a": 0.1, "b": 0.2}},
                "graph_visualization_artifacts": [{"artifact_id": "layout"}],
            },
        },
    )
    population = Population(
        id="runtime-population",
        scenario_id=scenario.id,
        size=2,
        agent_ids=["a", "b"],
        metadata={"state": {"value": [0, 1], "financial_stability": [1.0, 2.0]}},
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

    run = run_simulation(scenario, population, pack)

    result = run.outputs["evidence_bounded_transition_results"][0]
    assert result["data_lineage"][0]["content_hash"] == "a" * 64
    assert "probability_of_harm" in result
    assert run.outputs["statistical_baseline"]["baseline_method"] == "mean_prior_effect"
    assert run.outputs["run_data_manifest"]["dataset_references"]
    assert run.outputs["kpis"][0][
        "evidence_bounded_transition_engine.evidence_bounded.financial_stability.expected_effect"
    ]


def test_runtime_fails_closed_when_evidence_bounded_mode_has_no_target_trials() -> None:
    scenario = Scenario(
        id="runtime-target-trial-missing",
        domain_pack_id="generic-pack",
        name="Runtime target trial missing",
        parameters={"require_evidence_bounded_transitions": True},
    )
    population = Population(id="runtime-population", scenario_id=scenario.id, size=0)
    pack = DomainPack(
        id="generic-pack",
        name="Generic Pack",
        version="0.1.0",
        state_schema={"type": "object"},
    )

    with pytest.raises(ValueError, match="requires target_trials"):
        run_simulation(scenario, population, pack)


def test_target_trial_compiler_reads_scenario_contract() -> None:
    scenario = Scenario(
        id="job_training_retraining",
        domain_pack_id="generic-pack",
        name="Scenario target trial",
        parameters={"target_trials": [target_trial_payload_fixture_only()]},
    )

    specs = compile_scenario_target_trials(scenario)

    assert specs[0].scenario_id == "job_training_retraining"


def test_target_trial_compiler_rejects_scenario_mismatch() -> None:
    scenario = Scenario(
        id="different-scenario",
        domain_pack_id="generic-pack",
        name="Scenario mismatch",
        parameters={"target_trials": [target_trial_payload_fixture_only()]},
    )

    with pytest.raises(ValueError, match="scenario_id must match"):
        compile_scenario_target_trials(scenario)


def test_target_trial_compiler_rejects_duplicate_outcome_domains() -> None:
    first = target_trial_payload_fixture_only()
    second = target_trial_payload_fixture_only()
    second["transition_model_id"] = "another_transition"

    with pytest.raises(ValueError, match="duplicate outcome_domain"):
        compile_scenario_target_trials([first, second])


def test_runtime_requires_intervention_priors_feature_reference(tmp_path: Path) -> None:
    target_trial = target_trial_payload_fixture_only()
    del target_trial["evidence_prior"]["feature_dataset_reference"]  # type: ignore[index]
    scenario = Scenario(
        id="job_training_retraining",
        domain_pack_id="generic-pack",
        name="Runtime target trial missing feature reference",
        parameters={"target_trials": [target_trial]},
    )
    population = Population(id="runtime-population", scenario_id=scenario.id, size=0)
    pack = DomainPack(id="generic-pack", name="Generic Pack", version="0.1.0", state_schema={})

    with pytest.raises(ValueError, match="features.intervention_effect_size_priors_v1"):
        run_simulation(scenario, population, pack)


def test_runtime_fails_closed_for_vectorized_transitions_without_legacy_opt_in() -> None:
    scenario = Scenario(
        id="legacy-vectorized",
        domain_pack_id="generic-pack",
        name="Legacy vectorized",
    )
    population = Population(id="runtime-population", scenario_id=scenario.id, size=0)
    pack = DomainPack(
        id="generic-pack",
        name="Generic Pack",
        version="0.1.0",
        state_schema={},
        transition_models=[
            TransitionModel(
                id="increment",
                version="0.1.0",
                entrypoint="fw_kernel.testing_transitions.increment_value",
            )
        ],
    )

    with pytest.raises(ValueError, match="explicit legacy opt-in"):
        run_simulation(scenario, population, pack)


def test_domain_transition_model_cards_exist() -> None:
    for slug in [
        "happiness-transition",
        "health-transition",
        "meaning-transition",
        "character-transition",
        "relationships-transition",
        "financial-stability-transition",
    ]:
        card = (ROOT / "docs" / "model-cards" / f"{slug}.md").read_text(encoding="utf-8")
        assert "dataset_reference" in card
        assert "probability of harm" in card
        assert "cannot create causal effect sizes" in card
