from __future__ import annotations

import numpy as np
import pytest

from fw_kernel import (
    compile_target_trial_spec,
    exposure_measure_disagreement,
    graph_layer_ablation,
    omitted_confounding_e_value,
    posterior_draws,
    prior_sensitivity,
    run_statistical_baseline,
    seed_stability,
)

from target_trial_fixture_only import target_trial_payload_fixture_only


def _prior():
    return compile_target_trial_spec(target_trial_payload_fixture_only()).evidence_prior


def test_posterior_draws_are_seed_reproducible() -> None:
    first = posterior_draws(_prior(), seed=22, draws=100)
    second = posterior_draws(_prior(), seed=22, draws=100)

    assert np.array_equal(first, second)


def test_sensitivity_modules_emit_expected_hooks() -> None:
    prior = _prior()

    assert prior_sensitivity(prior)["plus_one_uncertainty"] > prior.effect_size
    assert omitted_confounding_e_value(prior.effect_size) >= 1
    assert seed_stability(prior, seeds=[1, 2], draws=50)["seed_count"] == 2
    assert exposure_measure_disagreement({"a": 0.1, "b": 0.4})["range"] == 0.30000000000000004
    ablation = graph_layer_ablation({"peer": 0.02}, [{"artifact_id": "layout"}])
    assert ablation["causal_delta_from_graph_visualization"] == 0.0
    assert ablation["graph_artifact_count"] == 1.0


def test_statistical_baseline_requires_same_evidence_references() -> None:
    spec = compile_target_trial_spec(target_trial_payload_fixture_only())

    with pytest.raises(ValueError, match="missing target-trial evidence references"):
        run_statistical_baseline(
            {
                "run_id": "run_fixture_only",
                "dataset_references": [
                    {
                        "canonical_dataset_name": "features.intervention_effect_size_priors_v1",
                        "version": "fixture-0.1",
                        "content_hash": "b" * 64,
                    }
                ],
            },
            [spec],
        )
