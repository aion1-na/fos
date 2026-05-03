from __future__ import annotations

from dataclasses import dataclass
from math import exp, sqrt
from typing import Any, Literal

import numpy as np
from fw_contracts import DatasetReference, Scenario
from pydantic import BaseModel, Field, model_validator


class EvidencePrior(BaseModel):
    claim_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    dataset_reference: DatasetReference
    effect_size: float
    uncertainty: float = Field(gt=0)
    citation: str = Field(min_length=1)
    risk_of_bias: Literal["low", "medium", "high"]
    transportability: Literal["low", "medium", "high"]
    review_status: Literal["draft", "advisor_reviewed", "rejected", "superseded"]
    effect_validated: bool = False
    feature_dataset_reference: DatasetReference | None = None

    @model_validator(mode="after")
    def reject_external_tool_provenance(self) -> "EvidencePrior":
        blocked_sources = ("concordia", "fos_graph", "mirofish", "graph")
        names = [self.dataset_reference.canonical_dataset_name, self.source_id]
        if self.feature_dataset_reference is not None:
            names.append(self.feature_dataset_reference.canonical_dataset_name)
        if any(blocked in name.lower() for name in names for blocked in blocked_sources):
            raise ValueError("evidence priors cannot originate from external tool artifacts")
        return self


class TargetTrialSpec(BaseModel):
    scenario_id: str = Field(min_length=1)
    transition_model_id: str = Field(min_length=1)
    target_population: str = Field(min_length=1)
    treatment: str = Field(min_length=1)
    comparator: str = Field(min_length=1)
    outcome_domain: str = Field(min_length=1)
    estimand: str = Field(default="average_treatment_effect", min_length=1)
    evidence_prior: EvidencePrior

    @model_validator(mode="after")
    def require_dataset_reference(self) -> "TargetTrialSpec":
        if not self.evidence_prior.dataset_reference.content_hash:
            raise ValueError("target-trial evidence prior requires dataset_reference")
        if (
            self.evidence_prior.review_status != "advisor_reviewed"
            or not self.evidence_prior.effect_validated
        ):
            raise ValueError("target-trial causal transitions require validated advisor-reviewed priors")
        return self


class TransitionInputBundle(BaseModel):
    measurement_inputs: dict[str, Any] = Field(default_factory=dict)
    network_effects: dict[str, float] = Field(default_factory=dict)
    concordia_cognition_traces: list[dict[str, Any]] = Field(default_factory=list)
    graph_visualization_artifacts: list[dict[str, Any]] = Field(default_factory=list)


class TransitionKernelResult(BaseModel):
    scenario_id: str
    transition_model_id: str
    outcome_domain: str
    expected_effect: float
    uncertainty_interval: dict[str, float]
    probability_of_harm: float
    subgroup_heterogeneity: dict[str, Any]
    data_lineage: list[dict[str, str]]
    sensitivity: dict[str, Any]
    separated_inputs: dict[str, Any]


def compile_target_trial_spec(payload: dict[str, Any]) -> TargetTrialSpec:
    return TargetTrialSpec.model_validate(payload)


def compile_scenario_target_trials(payloads: Scenario | list[dict[str, Any]]) -> list[TargetTrialSpec]:
    scenario_id: str | None = None
    if isinstance(payloads, Scenario):
        scenario_id = payloads.id
        raw_payloads = payloads.parameters.get("target_trials", [])
        if not isinstance(raw_payloads, list):
            raise TypeError("scenario.parameters['target_trials'] must be a list")
        payloads = raw_payloads
    if not payloads:
        raise ValueError("transition engine requires at least one target-trial evidence prior")
    specs = [compile_target_trial_spec(payload) for payload in payloads]
    if scenario_id is not None:
        for spec in specs:
            if spec.scenario_id != scenario_id:
                raise ValueError("target-trial scenario_id must match parent Scenario.id")
    outcome_domains = [spec.outcome_domain for spec in specs]
    duplicate_domains = {
        domain for domain in outcome_domains if outcome_domains.count(domain) > 1
    }
    if duplicate_domains:
        raise ValueError("target-trial specs must not contain duplicate outcome_domain values")
    return specs


def _reject_external_causal_effects(bundle: TransitionInputBundle) -> None:
    blocked_exact_keys = {"ate"}
    blocked_terms = (
        "causal",
        "coefficient",
        "counterfactual",
        "delta",
        "effect",
        "estimate",
        "impact",
        "lift",
    )
    blocked_text_terms = (
        "causal effect",
        "effect size",
        "estimated effect",
        "expected effect",
        "treatment effect",
    )

    def contains_blocked_key(payload: Any) -> bool:
        if isinstance(payload, dict):
            for key, value in payload.items():
                normalized = str(key).replace("_", "").replace("-", "").lower()
                if normalized == "maysetcausaleffectsize" and value is False:
                    continue
                if normalized in blocked_exact_keys or any(term in normalized for term in blocked_terms):
                    return True
                if contains_blocked_key(value):
                    return True
        if isinstance(payload, list):
            return any(contains_blocked_key(item) for item in payload)
        if isinstance(payload, str):
            normalized_value = payload.lower()
            return any(term in normalized_value for term in blocked_text_terms)
        return False

    for lane_name, artifacts in {
        "Concordia cognition traces": bundle.concordia_cognition_traces,
        "FOS Graph artifacts": bundle.graph_visualization_artifacts,
    }.items():
        for artifact in artifacts:
            if contains_blocked_key(artifact):
                raise ValueError(f"{lane_name} cannot set causal effect sizes")


def posterior_draws(prior: EvidencePrior, *, seed: int, draws: int = 1000) -> np.ndarray:
    if draws <= 0:
        raise ValueError("posterior draw count must be positive")
    rng = np.random.default_rng(seed)
    return rng.normal(loc=prior.effect_size, scale=prior.uncertainty, size=draws)


def prior_sensitivity(prior: EvidencePrior) -> dict[str, float]:
    return {
        "minus_one_uncertainty": prior.effect_size - prior.uncertainty,
        "plus_one_uncertainty": prior.effect_size + prior.uncertainty,
    }


def omitted_confounding_e_value(effect_size: float) -> float:
    risk_ratio_proxy = exp(abs(effect_size))
    return risk_ratio_proxy + sqrt(risk_ratio_proxy * max(risk_ratio_proxy - 1.0, 0.0))


def seed_stability(prior: EvidencePrior, *, seeds: list[int], draws: int = 250) -> dict[str, float]:
    means = [float(np.mean(posterior_draws(prior, seed=seed, draws=draws))) for seed in seeds]
    return {
        "seed_count": float(len(seeds)),
        "mean_of_seed_means": float(np.mean(means)),
        "variance_of_seed_means": float(np.var(means)),
    }


def exposure_measure_disagreement(measures: dict[str, float]) -> dict[str, float]:
    values = list(measures.values())
    if not values:
        return {"measure_count": 0.0, "range": 0.0, "standard_deviation": 0.0}
    return {
        "measure_count": float(len(values)),
        "range": float(max(values) - min(values)),
        "standard_deviation": float(np.std(values)),
    }


def graph_layer_ablation(
    network_effects: dict[str, float],
    graph_visualization_artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, float]:
    total = float(sum(network_effects.values()))
    return {
        "with_graph_layer": total,
        "without_graph_visualization_artifacts": total,
        "graph_artifact_count": float(len(graph_visualization_artifacts or [])),
        "causal_delta_from_graph_visualization": 0.0,
    }


def subgroup_heterogeneity_summary(
    prior: EvidencePrior,
    draws: np.ndarray,
) -> dict[str, Any]:
    mean = float(np.mean(draws))
    return {
        "status": "not_estimated",
        "overall_expected_effect": mean,
        "subgroup_estimates": {},
        "reason": (
            "No validated subgroup-specific evidence prior was supplied; "
            "heterogeneity is withheld rather than synthesized."
        ),
        "transportability": prior.transportability,
    }


@dataclass(frozen=True)
class EvidenceBoundedTransitionEngine:
    posterior_draw_count: int = 1000
    stability_seeds: tuple[int, ...] = (11, 17, 23)

    def run(
        self,
        spec: TargetTrialSpec,
        bundle: TransitionInputBundle | None = None,
        *,
        seed: int,
    ) -> TransitionKernelResult:
        bundle = bundle or TransitionInputBundle()
        _reject_external_causal_effects(bundle)
        prior = spec.evidence_prior
        draws = posterior_draws(prior, seed=seed, draws=self.posterior_draw_count)
        lower, upper = np.quantile(draws, [0.025, 0.975])
        subgroup_heterogeneity = subgroup_heterogeneity_summary(prior, draws)
        data_lineage = [prior.dataset_reference.model_dump(mode="json")]
        if prior.feature_dataset_reference is not None:
            data_lineage.append(prior.feature_dataset_reference.model_dump(mode="json"))
        return TransitionKernelResult(
            scenario_id=spec.scenario_id,
            transition_model_id=spec.transition_model_id,
            outcome_domain=spec.outcome_domain,
            expected_effect=float(np.mean(draws)),
            uncertainty_interval={"lower": float(lower), "upper": float(upper)},
            probability_of_harm=float(np.mean(draws < 0)),
            subgroup_heterogeneity=subgroup_heterogeneity,
            data_lineage=data_lineage,
            sensitivity={
                "prior_sensitivity": prior_sensitivity(prior),
                "omitted_confounding_e_value": omitted_confounding_e_value(prior.effect_size),
                "seed_stability": seed_stability(
                    prior,
                    seeds=list(self.stability_seeds),
                    draws=max(50, self.posterior_draw_count // 4),
                ),
                "exposure_measure_disagreement": exposure_measure_disagreement(
                    bundle.measurement_inputs.get("exposure_measures", {})
                ),
                "graph_layer_ablation": graph_layer_ablation(
                    bundle.network_effects,
                    bundle.graph_visualization_artifacts,
                ),
            },
            separated_inputs={
                "measurement": bundle.measurement_inputs,
                "causal_transition_prior": prior.model_dump(mode="json"),
                "network_effects": bundle.network_effects,
                "concordia_cognition_traces": bundle.concordia_cognition_traces,
                "graph_visualization_artifacts": bundle.graph_visualization_artifacts,
            },
        )


def run_statistical_baseline(
    run_manifest: dict[str, Any],
    specs: list[TargetTrialSpec],
) -> dict[str, Any]:
    manifest_references = run_manifest.get("dataset_references")
    if not manifest_references:
        raise ValueError("baseline requires run manifest dataset_references")
    manifest_keys = {
        (
            reference["canonical_dataset_name"],
            reference["version"],
            reference["content_hash"],
        )
        for reference in manifest_references
    }
    missing = [
        spec.evidence_prior.dataset_reference.as_tuple()
        for spec in specs
        if spec.evidence_prior.dataset_reference.as_tuple() not in manifest_keys
    ]
    if missing:
        raise ValueError("baseline run manifest is missing target-trial evidence references")
    priors = [spec.evidence_prior for spec in specs]
    draws = np.asarray(
        [
            np.mean(posterior_draws(prior, seed=index, draws=250))
            for index, prior in enumerate(priors)
        ]
    )
    lower, upper = np.quantile(draws, [0.025, 0.975])
    return {
        "baseline_method": "mean_prior_effect",
        "run_id": run_manifest.get("run_id"),
        "dataset_references": manifest_references,
        "expected_effect": float(np.mean(draws)),
        "uncertainty_interval": {"lower": float(lower), "upper": float(upper)},
        "probability_of_harm": float(np.mean(draws < 0)),
        "subgroup_heterogeneity": {
            "status": "not_estimated",
            "subgroup_estimates": {},
            "reason": "Statistical baseline uses pooled prior means only.",
        },
        "data_lineage": [
            reference
            for prior in priors
            for reference in (
                prior.dataset_reference.model_dump(mode="json"),
                (
                    prior.feature_dataset_reference.model_dump(mode="json")
                    if prior.feature_dataset_reference is not None
                    else None
                ),
            )
            if reference is not None
        ],
        "scenario_count": len(specs),
    }
