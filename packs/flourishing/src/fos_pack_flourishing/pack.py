from __future__ import annotations

import numpy as np
from fw_contracts import (
    CONTRACTS_VERSION,
    DomainPack,
    OntologyRef,
    Population,
    RenderHints,
    Scenario,
    SpawnSpec,
    TransitionModel,
    ValidationSuite,
    assert_contracts_version,
)

from fos_pack_flourishing.interventions import JOB_TRAINING, MENTORING, PAID_LEAVE
from fos_pack_flourishing.state_schema import STATE_FIELD_COUNT, state_schema

PACK_ID = "flourishing"
PACK_VERSION = "0.1.0"


TRANSITION_ENTRYPOINTS = {
    "income": "fos_pack_flourishing.transitions.income.vectorized_income",
    "identity": "fos_pack_flourishing.transitions.identity.vectorized_identity",
    "social-ties": "fos_pack_flourishing.transitions.social_ties.vectorized_social_ties",
    "time-structure": "fos_pack_flourishing.transitions.time_structure.vectorized_time_structure",
    "health": "fos_pack_flourishing.transitions.health.vectorized_health",
    "meaning": "fos_pack_flourishing.transitions.meaning.vectorized_meaning",
}


def build_pack() -> DomainPack:
    pack = DomainPack(
        id=PACK_ID,
        name="Flourishing",
        version=PACK_VERSION,
        contracts_version=CONTRACTS_VERSION,
        state_schema=state_schema(),
        ontology=[
            OntologyRef(id="domain-score", version="0.1.0"),
            OntologyRef(id="latent-risk", version="0.1.0"),
            OntologyRef(id="childhood-predictor", version="0.1.0"),
            OntologyRef(id="current-context", version="0.1.0"),
            OntologyRef(id="institutional-membership", version="0.1.0"),
        ],
        transition_models=[
            TransitionModel(
                id=transition_id,
                version=PACK_VERSION,
                entrypoint=entrypoint,
                parameters_schema={"type": "object", "additionalProperties": True},
            )
            for transition_id, entrypoint in TRANSITION_ENTRYPOINTS.items()
        ],
        validation_suites=[
            ValidationSuite(
                id="flourishing-validation-v0",
                checks=["heldout-wave-backtest", "e-value", "drift-check"],
                parameters={"max_backtest_mse": 0.01, "max_mean_drift": 0.05},
            )
        ],
        render_hints=RenderHints(
            preferred_views=["six-domain-radar", "agent-distribution"],
            encodings={
                "domain_color_ramps": {
                    "happiness": ["#f7fbff", "#6baed6", "#08306b"],
                    "health": ["#f7fcf5", "#74c476", "#00441b"],
                    "meaning": ["#fff7ec", "#fdae6b", "#7f2704"],
                    "character": ["#fcfbfd", "#9e9ac8", "#3f007d"],
                    "relationships": ["#fff5f0", "#fb6a4a", "#67000d"],
                    "financial": ["#f7fcfd", "#41b6c4", "#253494"],
                },
                "radar_chart": {
                    "type": "radar",
                    "axes": [
                        "happiness",
                        "health",
                        "meaning",
                        "character",
                        "relationships",
                        "financial",
                    ],
                    "range": [0, 1],
                },
            },
        ),
    )
    assert_contracts_version(pack.contracts_version)
    return pack


PACK = build_pack()
INTERVENTIONS = [PAID_LEAVE, JOB_TRAINING, MENTORING]


def _bounded(rng: np.random.Generator, count: int, low: float = 0.2, high: float = 0.9) -> list[float]:
    return rng.uniform(low, high, size=count).round(6).tolist()


def _integers(rng: np.random.Generator, count: int, low: int, high: int) -> list[int]:
    return rng.integers(low, high + 1, size=count).astype(int).tolist()


def spawn_population_state(spec: SpawnSpec) -> dict[str, list[object]]:
    seed = int(spec.state_seed.get("seed", 0))
    rng = np.random.default_rng(seed)
    count = spec.count
    employment_values = np.asarray(["student", "employed", "unemployed", "caregiver", "retired"])
    employment = employment_values[rng.integers(0, employment_values.shape[0], size=count)].tolist()
    state: dict[str, list[object]] = {
        "happiness": _bounded(rng, count),
        "health": _bounded(rng, count),
        "meaning": _bounded(rng, count),
        "character": _bounded(rng, count),
        "relationships": _bounded(rng, count),
        "financial": _bounded(rng, count),
        "resilience": _bounded(rng, count),
        "loneliness_risk": _bounded(rng, count, 0.05, 0.55),
        "childhood_household_income": _bounded(rng, count),
        "childhood_parent_education": _bounded(rng, count),
        "childhood_neighborhood_safety": _bounded(rng, count),
        "childhood_health_access": _bounded(rng, count),
        "childhood_food_security": _bounded(rng, count),
        "childhood_housing_stability": _bounded(rng, count),
        "childhood_school_quality": _bounded(rng, count),
        "childhood_caregiver_support": _bounded(rng, count),
        "childhood_adverse_events": _integers(rng, count, 0, 5),
        "childhood_social_trust": _bounded(rng, count),
        "childhood_mobility_count": _integers(rng, count, 0, 8),
        "childhood_rurality": _bounded(rng, count, 0.0, 1.0),
        "age": _integers(rng, count, 18, 82),
        "education_years": _integers(rng, count, 10, 20),
        "employment_status": employment,
        "income_percentile": _bounded(rng, count),
        "debt_burden": _bounded(rng, count, 0.0, 0.8),
        "savings_buffer_months": rng.uniform(0.0, 18.0, size=count).round(6).tolist(),
        "housing_stability": _bounded(rng, count),
        "food_security": _bounded(rng, count),
        "commute_minutes": rng.uniform(0.0, 90.0, size=count).round(6).tolist(),
        "work_hours": rng.uniform(0.0, 60.0, size=count).round(6).tolist(),
        "care_hours": rng.uniform(0.0, 45.0, size=count).round(6).tolist(),
        "sleep_hours": rng.uniform(5.0, 9.5, size=count).round(6).tolist(),
        "exercise_minutes": rng.uniform(0.0, 80.0, size=count).round(6).tolist(),
        "preventive_care_access": _bounded(rng, count),
        "chronic_condition_count": _integers(rng, count, 0, 4),
        "stress_load": _bounded(rng, count, 0.05, 0.85),
        "perceived_safety": _bounded(rng, count),
        "civic_trust": _bounded(rng, count),
        "neighborhood_cohesion": _bounded(rng, count),
        "digital_access": _bounded(rng, count),
        "schedule_volatility": _bounded(rng, count, 0.0, 0.8),
        "autonomy_at_work": _bounded(rng, count),
        "skill_match": _bounded(rng, count),
        "job_security": _bounded(rng, count),
        "benefits_access": _bounded(rng, count),
        "social_contact_frequency": _bounded(rng, count),
        "trusted_friend_count": _integers(rng, count, 0, 12),
        "household_size": _integers(rng, count, 1, 6),
        "caregiving_support": _bounded(rng, count),
        "partner_support": _bounded(rng, count),
        "family_contact": _bounded(rng, count),
        "community_participation": _bounded(rng, count),
        "religious_service_frequency": _bounded(rng, count, 0.0, 1.0),
        "volunteering_hours": rng.uniform(0.0, 16.0, size=count).round(6).tolist(),
        "purpose_clarity": _bounded(rng, count),
        "values_alignment": _bounded(rng, count),
        "learning_hours": rng.uniform(0.0, 14.0, size=count).round(6).tolist(),
        "creative_hours": rng.uniform(0.0, 12.0, size=count).round(6).tolist(),
        "nature_access": _bounded(rng, count),
        "mentor_access": _bounded(rng, count),
        "institution_school": (rng.random(count) > 0.65).tolist(),
        "institution_employer": (rng.random(count) > 0.35).tolist(),
        "institution_healthcare": (rng.random(count) > 0.20).tolist(),
        "institution_bank": (rng.random(count) > 0.25).tolist(),
        "institution_housing_program": (rng.random(count) > 0.80).tolist(),
        "institution_childcare": (rng.random(count) > 0.75).tolist(),
        "institution_transport": (rng.random(count) > 0.45).tolist(),
        "institution_religious": (rng.random(count) > 0.70).tolist(),
        "institution_civic": (rng.random(count) > 0.68).tolist(),
        "institution_training": (rng.random(count) > 0.78).tolist(),
    }
    if len(state) != STATE_FIELD_COUNT:
        raise AssertionError(f"expected {STATE_FIELD_COUNT} state fields, got {len(state)}")
    return state


def build_population(
    scenario: Scenario,
    spec: SpawnSpec,
) -> Population:
    return Population(
        id=spec.population_id,
        scenario_id=scenario.id,
        size=spec.count,
        agent_ids=[f"{spec.population_id}-{index}" for index in range(spec.count)],
        metadata={"state": spawn_population_state(spec)},
    )
