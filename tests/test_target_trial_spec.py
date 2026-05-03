from __future__ import annotations

import pytest

from fw_kernel import TargetTrialSpec, compile_scenario_target_trials, compile_target_trial_spec
from target_trial_fixture_only import target_trial_payload_fixture_only


def test_target_trial_spec_requires_evidence_prior_dataset_reference() -> None:
    payload = target_trial_payload_fixture_only()
    del payload["evidence_prior"]["dataset_reference"]  # type: ignore[index]

    with pytest.raises(ValueError):
        TargetTrialSpec.model_validate(payload)


def test_scenario_compiler_builds_target_trial_specs() -> None:
    spec = compile_target_trial_spec(target_trial_payload_fixture_only())
    compiled = compile_scenario_target_trials([target_trial_payload_fixture_only()])

    assert spec.estimand == "average_treatment_effect"
    assert compiled[0].evidence_prior.dataset_reference.as_tuple() == (
        "intervention_literature.job_training",
        "request-status-v0.1",
        "a" * 64,
    )
    assert compiled[0].evidence_prior.feature_dataset_reference.as_tuple() == (
        "features.intervention_effect_size_priors_v1",
        "fixture-0.1",
        "b" * 64,
    )


def test_scenario_compiler_fails_closed_without_priors() -> None:
    with pytest.raises(ValueError, match="requires at least one target-trial evidence prior"):
        compile_scenario_target_trials([])


def test_target_trial_rejects_unreviewed_or_unvalidated_priors() -> None:
    payload = target_trial_payload_fixture_only()
    payload["evidence_prior"]["effect_validated"] = False  # type: ignore[index]

    with pytest.raises(ValueError, match="validated advisor-reviewed priors"):
        TargetTrialSpec.model_validate(payload)
