from __future__ import annotations

import pytest
from pathlib import Path

from fw_kernel import EvidenceBoundedTransitionEngine, TransitionInputBundle, compile_target_trial_spec
from fos_data_pipelines.evidence_graph.claims import priors_for_concordia_scene_compiler

from target_trial_fixture_only import target_trial_payload_fixture_only

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = (
    ROOT
    / "packages"
    / "data-pipelines"
    / "fixtures"
    / "evidence_graph"
    / "evidence_claims_fixture_only.json"
)


def test_concordia_cognition_trace_cannot_set_causal_effect_size() -> None:
    with pytest.raises(ValueError, match="Concordia cognition traces cannot set causal effect sizes"):
        EvidenceBoundedTransitionEngine().run(
            compile_target_trial_spec(target_trial_payload_fixture_only()),
            TransitionInputBundle(
                concordia_cognition_traces=[
                    {"artifact_id": "concordia-scene", "causal_effect_size": 0.5}
                ],
            ),
            seed=1,
        )


def test_graph_visualization_artifact_cannot_set_effect_size() -> None:
    with pytest.raises(ValueError, match="FOS Graph artifacts cannot set causal effect sizes"):
        EvidenceBoundedTransitionEngine().run(
            compile_target_trial_spec(target_trial_payload_fixture_only()),
            TransitionInputBundle(
                graph_visualization_artifacts=[{"artifact_id": "layout", "effect_size": 0.5}],
            ),
            seed=1,
        )


def test_nested_camel_case_tool_effect_keys_are_rejected() -> None:
    with pytest.raises(ValueError, match="Concordia cognition traces cannot set causal effect sizes"):
        EvidenceBoundedTransitionEngine().run(
            compile_target_trial_spec(target_trial_payload_fixture_only()),
            TransitionInputBundle(
                concordia_cognition_traces=[
                    {"artifact_id": "scene", "nested": {"causalEffectSize": 0.4}}
                ],
            ),
            seed=1,
        )


def test_external_tool_delta_estimates_are_rejected() -> None:
    with pytest.raises(ValueError, match="FOS Graph artifacts cannot set causal effect sizes"):
        EvidenceBoundedTransitionEngine().run(
            compile_target_trial_spec(target_trial_payload_fixture_only()),
            TransitionInputBundle(
                graph_visualization_artifacts=[
                    {"artifact_id": "layout", "analytics": {"delta": 0.2, "estimate": 0.3}}
                ],
            ),
            seed=1,
        )


def test_concordia_qualitative_prior_context_is_allowed_without_numeric_effects() -> None:
    trace = priors_for_concordia_scene_compiler("job_training_retraining", CLAIMS)[0]

    result = EvidenceBoundedTransitionEngine().run(
        compile_target_trial_spec(target_trial_payload_fixture_only()),
        TransitionInputBundle(concordia_cognition_traces=[trace]),
        seed=1,
    )

    assert result.separated_inputs["concordia_cognition_traces"][0]["treatment"]
