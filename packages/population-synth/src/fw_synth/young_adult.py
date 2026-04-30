from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
from fw_contracts import SpawnSpec

from fw_synth.errors import PopulationSynthError
from fw_synth.ipf import rake
from fw_synth.networks.household import form_households
from fw_synth.networks.small_world import watts_strogatz
from fw_synth.snapshot import SnapshotArtifact, write_snapshot
from fw_synth.store import SynthStore

REQUIRED_REFERENCE_NAMES = frozenset(
    {
        "acs_pums_young_adults",
        "cps_young_adults",
        "gfs_wave12_panel_non_sensitive",
    }
)

CALIBRATION_DIMENSIONS = (
    "age_band",
    "education",
    "employment_status",
    "household_type",
    "income_band",
    "geography",
    "occupation_group",
)

STATE_FIELDS = (
    "happiness",
    "health",
    "meaning",
    "character",
    "relationships",
    "financial",
    "resilience",
    "loneliness_risk",
    "childhood_household_income",
    "childhood_parent_education",
    "childhood_neighborhood_safety",
    "childhood_health_access",
    "childhood_food_security",
    "childhood_housing_stability",
    "childhood_school_quality",
    "childhood_caregiver_support",
    "childhood_adverse_events",
    "childhood_social_trust",
    "childhood_mobility_count",
    "childhood_rurality",
    "age",
    "education_years",
    "employment_status",
    "income_percentile",
    "debt_burden",
    "savings_buffer_months",
    "housing_stability",
    "food_security",
    "commute_minutes",
    "work_hours",
    "care_hours",
    "sleep_hours",
    "exercise_minutes",
    "preventive_care_access",
    "chronic_condition_count",
    "stress_load",
    "perceived_safety",
    "civic_trust",
    "neighborhood_cohesion",
    "digital_access",
    "schedule_volatility",
    "autonomy_at_work",
    "skill_match",
    "job_security",
    "benefits_access",
    "social_contact_frequency",
    "trusted_friend_count",
    "household_size",
    "caregiving_support",
    "partner_support",
    "family_contact",
    "community_participation",
    "religious_service_frequency",
    "volunteering_hours",
    "purpose_clarity",
    "values_alignment",
    "learning_hours",
    "creative_hours",
    "nature_access",
    "mentor_access",
    "institution_school",
    "institution_employer",
    "institution_healthcare",
    "institution_bank",
    "institution_housing_program",
    "institution_childcare",
    "institution_transport",
    "institution_religious",
    "institution_civic",
    "institution_training",
)

PRIOR_FILLED_FIELDS = (
    "happiness",
    "health",
    "meaning",
    "character",
    "relationships",
    "resilience",
    "loneliness_risk",
    "childhood_household_income",
    "childhood_parent_education",
    "childhood_neighborhood_safety",
    "childhood_health_access",
    "childhood_food_security",
    "childhood_housing_stability",
    "childhood_school_quality",
    "childhood_caregiver_support",
    "childhood_social_trust",
    "debt_burden",
    "housing_stability",
    "food_security",
    "preventive_care_access",
    "stress_load",
    "perceived_safety",
    "civic_trust",
    "neighborhood_cohesion",
    "digital_access",
    "schedule_volatility",
    "autonomy_at_work",
    "skill_match",
    "job_security",
    "benefits_access",
    "social_contact_frequency",
    "caregiving_support",
    "partner_support",
    "family_contact",
    "community_participation",
    "religious_service_frequency",
    "purpose_clarity",
    "values_alignment",
    "nature_access",
    "mentor_access",
)


@dataclass(frozen=True)
class MarginalBundle:
    path: Path
    content_hash: str
    dataset_reference: dict[str, str]
    source_references: list[dict[str, str]]
    marginals: dict[str, dict[str, float]]
    priors: dict[str, Any]


def load_marginal_bundle(path: str | Path, *, demo_mode: bool = False) -> MarginalBundle:
    marginal_path = Path(path)
    payload = json.loads(marginal_path.read_text(encoding="utf-8"))
    source_references = list(payload.get("source_references", []))
    present = {str(reference.get("canonical_dataset_name")) for reference in source_references}
    missing = sorted(REQUIRED_REFERENCE_NAMES - present)
    if missing and not demo_mode:
        raise PopulationSynthError(
            "young-adult synthesis requires ACS, CPS, and GFS dataset references; "
            f"missing {', '.join(missing)}"
        )

    marginals = payload.get("marginals")
    if not isinstance(marginals, dict):
        raise PopulationSynthError("marginal bundle must contain a marginals object")
    for dimension in CALIBRATION_DIMENSIONS:
        if dimension not in marginals or not marginals[dimension]:
            raise PopulationSynthError(f"missing required marginal dimension {dimension!r}")

    content = marginal_path.read_bytes()
    dataset_reference = dict(payload.get("dataset_reference", {}))
    return MarginalBundle(
        path=marginal_path,
        content_hash=sha256(content).hexdigest(),
        dataset_reference=dataset_reference,
        source_references=source_references,
        marginals={
            str(name): {str(key): float(value) for key, value in values.items()}
            for name, values in marginals.items()
        },
        priors=dict(payload.get("priors", {})),
    )


def _targets(bundle: MarginalBundle, count: int) -> dict[str, dict[str, float]]:
    targets: dict[str, dict[str, float]] = {}
    for dimension in CALIBRATION_DIMENSIONS:
        values = bundle.marginals[dimension]
        total = sum(values.values())
        if total <= 0:
            raise PopulationSynthError(f"marginal dimension {dimension!r} has no mass")
        targets[dimension] = {
            category: (share / total) * count for category, share in values.items()
        }
    return targets


def _support(marginals: dict[str, dict[str, float]]) -> dict[str, np.ndarray]:
    rows = list(product(*(sorted(marginals[dimension]) for dimension in CALIBRATION_DIMENSIONS)))
    return {
        dimension: np.asarray([row[index] for row in rows], dtype=str)
        for index, dimension in enumerate(CALIBRATION_DIMENSIONS)
    }


def _sample_categories(
    bundle: MarginalBundle, count: int, rng: np.random.Generator
) -> dict[str, np.ndarray]:
    support = _support(bundle.marginals)
    result = rake(
        np.ones(next(iter(support.values())).shape[0], dtype=float),
        dimensions=support,
        targets=_targets(bundle, count),
        threshold=1e-7,
    )
    probabilities = result.weights / np.sum(result.weights)
    selected = rng.choice(np.arange(probabilities.shape[0]), size=count, replace=True, p=probabilities)
    return {dimension: values[selected] for dimension, values in support.items()}


def _age(age_band: str, rng: np.random.Generator) -> int:
    low, high = age_band.split("-", 1)
    return int(rng.integers(int(low), int(high) + 1))


def _education_years(category: str, rng: np.random.Generator) -> int:
    ranges = {
        "less_than_hs": (10, 11),
        "high_school": (12, 12),
        "some_college": (13, 15),
        "bachelor_plus": (16, 20),
    }
    low, high = ranges[category]
    return int(rng.integers(low, high + 1))


def _income_percentile(category: str, rng: np.random.Generator) -> float:
    ranges = {
        "lt_25k": (0.02, 0.24),
        "25k_50k": (0.25, 0.49),
        "50k_100k": (0.50, 0.79),
        "100k_plus": (0.80, 0.98),
    }
    low, high = ranges[category]
    return float(round(rng.uniform(low, high), 6))


def _household_size(category: str, rng: np.random.Generator) -> int:
    ranges = {"alone": (1, 1), "family": (2, 5), "roommates": (2, 4)}
    low, high = ranges[category]
    return int(rng.integers(low, high + 1))


def _score(priors: dict[str, Any], name: str, rng: np.random.Generator) -> float:
    spec = priors.get(name, {})
    mean = float(spec.get("mean", 0.55))
    std = float(spec.get("std", 0.16))
    return float(round(np.clip(rng.normal(mean, std), 0.0, 1.0), 6))


def _hours(high: float, rng: np.random.Generator) -> float:
    return float(round(rng.uniform(0.0, high), 6))


def synthesize_young_adult_state(
    spec: SpawnSpec,
    seed: int,
    marginal_path: str | Path,
    *,
    demo_mode: bool = False,
) -> tuple[dict[str, list[object]], dict[str, Any], MarginalBundle, dict[str, np.ndarray]]:
    bundle = load_marginal_bundle(marginal_path, demo_mode=demo_mode)
    rng = np.random.default_rng(seed)
    categories = _sample_categories(bundle, spec.count, rng)
    state: dict[str, list[object]] = {field: [] for field in STATE_FIELDS}

    for index in range(spec.count):
        employment = str(categories["employment_status"][index])
        education = str(categories["education"][index])
        income = str(categories["income_band"][index])
        household = str(categories["household_type"][index])
        age = _age(str(categories["age_band"][index]), rng)
        work_hours = 0.0 if employment in {"student", "unemployed", "caregiver"} else _hours(50, rng)

        row: dict[str, object] = {
            "happiness": _score(bundle.priors, "happiness", rng),
            "health": _score(bundle.priors, "health", rng),
            "meaning": _score(bundle.priors, "meaning", rng),
            "character": _score(bundle.priors, "character", rng),
            "relationships": _score(bundle.priors, "relationships", rng),
            "financial": _income_percentile(income, rng),
            "resilience": _score(bundle.priors, "resilience", rng),
            "loneliness_risk": _score(bundle.priors, "loneliness_risk", rng),
            "childhood_household_income": _score(bundle.priors, "childhood_household_income", rng),
            "childhood_parent_education": _score(bundle.priors, "childhood_parent_education", rng),
            "childhood_neighborhood_safety": _score(bundle.priors, "childhood_neighborhood_safety", rng),
            "childhood_health_access": _score(bundle.priors, "childhood_health_access", rng),
            "childhood_food_security": _score(bundle.priors, "childhood_food_security", rng),
            "childhood_housing_stability": _score(bundle.priors, "childhood_housing_stability", rng),
            "childhood_school_quality": _score(bundle.priors, "childhood_school_quality", rng),
            "childhood_caregiver_support": _score(bundle.priors, "childhood_caregiver_support", rng),
            "childhood_adverse_events": int(rng.poisson(1.1)),
            "childhood_social_trust": _score(bundle.priors, "childhood_social_trust", rng),
            "childhood_mobility_count": int(rng.integers(0, 6)),
            "childhood_rurality": 1.0 if str(categories["geography"][index]) == "rural" else 0.0,
            "age": age,
            "education_years": _education_years(education, rng),
            "employment_status": employment,
            "income_percentile": _income_percentile(income, rng),
            "debt_burden": _score(bundle.priors, "debt_burden", rng),
            "savings_buffer_months": float(round(rng.uniform(0.0, 12.0), 6)),
            "housing_stability": _score(bundle.priors, "housing_stability", rng),
            "food_security": _score(bundle.priors, "food_security", rng),
            "commute_minutes": float(round(rng.uniform(0.0, 75.0), 6)),
            "work_hours": work_hours,
            "care_hours": _hours(35, rng),
            "sleep_hours": float(round(rng.uniform(5.5, 9.5), 6)),
            "exercise_minutes": _hours(75, rng),
            "preventive_care_access": _score(bundle.priors, "preventive_care_access", rng),
            "chronic_condition_count": int(rng.integers(0, 4)),
            "stress_load": _score(bundle.priors, "stress_load", rng),
            "perceived_safety": _score(bundle.priors, "perceived_safety", rng),
            "civic_trust": _score(bundle.priors, "civic_trust", rng),
            "neighborhood_cohesion": _score(bundle.priors, "neighborhood_cohesion", rng),
            "digital_access": _score(bundle.priors, "digital_access", rng),
            "schedule_volatility": _score(bundle.priors, "schedule_volatility", rng),
            "autonomy_at_work": _score(bundle.priors, "autonomy_at_work", rng),
            "skill_match": _score(bundle.priors, "skill_match", rng),
            "job_security": _score(bundle.priors, "job_security", rng),
            "benefits_access": _score(bundle.priors, "benefits_access", rng),
            "social_contact_frequency": _score(bundle.priors, "social_contact_frequency", rng),
            "trusted_friend_count": int(rng.integers(0, 10)),
            "household_size": _household_size(household, rng),
            "caregiving_support": _score(bundle.priors, "caregiving_support", rng),
            "partner_support": _score(bundle.priors, "partner_support", rng),
            "family_contact": _score(bundle.priors, "family_contact", rng),
            "community_participation": _score(bundle.priors, "community_participation", rng),
            "religious_service_frequency": _score(bundle.priors, "religious_service_frequency", rng),
            "volunteering_hours": _hours(12, rng),
            "purpose_clarity": _score(bundle.priors, "purpose_clarity", rng),
            "values_alignment": _score(bundle.priors, "values_alignment", rng),
            "learning_hours": _hours(14, rng),
            "creative_hours": _hours(12, rng),
            "nature_access": _score(bundle.priors, "nature_access", rng),
            "mentor_access": _score(bundle.priors, "mentor_access", rng),
            "institution_school": employment == "student",
            "institution_employer": employment == "employed",
            "institution_healthcare": True,
            "institution_bank": income != "lt_25k",
            "institution_housing_program": household != "alone" and income == "lt_25k",
            "institution_childcare": age >= 24 and household == "family",
            "institution_transport": True,
            "institution_religious": bool(rng.random() < 0.28),
            "institution_civic": bool(rng.random() < 0.32),
            "institution_training": education in {"some_college", "bachelor_plus"},
        }
        for field in STATE_FIELDS:
            state[field].append(row[field])

    diagnostics = calibration_diagnostics(categories, bundle, spec.count)
    return state, diagnostics, bundle, categories


def calibration_diagnostics(
    synthetic_categories: dict[str, np.ndarray], bundle: MarginalBundle, count: int
) -> dict[str, Any]:
    max_abs_std_diff = 0.0
    kl_divergence = 0.0
    covered = 0
    expected = 0
    by_dimension: dict[str, dict[str, Any]] = {}
    eps = 1e-12
    for dimension in CALIBRATION_DIMENSIONS:
        observed_counts = {
            category: int(np.sum(synthetic_categories[dimension] == category))
            for category in bundle.marginals[dimension]
        }
        total = sum(bundle.marginals[dimension].values())
        dimension_rows: dict[str, Any] = {}
        for category, share in bundle.marginals[dimension].items():
            target = share / total
            observed = observed_counts[category] / count
            variance = max(target * (1.0 - target) / count, eps)
            std_diff = (observed - target) / float(np.sqrt(variance))
            max_abs_std_diff = max(max_abs_std_diff, abs(std_diff))
            kl_divergence += target * float(np.log(max(target, eps) / max(observed, eps)))
            expected += 1
            if observed_counts[category] > 0:
                covered += 1
            dimension_rows[category] = {
                "target_share": round(target, 8),
                "observed_share": round(observed, 8),
                "standardized_difference": round(std_diff, 8),
            }
        by_dimension[dimension] = dimension_rows
    return {
        "feature_table": "features.synthetic_population_calibration_diagnostics",
        "max_absolute_standardized_difference": round(max_abs_std_diff, 8),
        "kl_divergence": round(kl_divergence, 8),
        "marginal_coverage": round(covered / expected, 8),
        "dimensions": by_dimension,
    }


def synthesize_young_adult_snapshot(
    spec: SpawnSpec,
    pack_version: str,
    seed: int,
    output_url: str,
    marginal_path: str | Path,
    *,
    demo_mode: bool = False,
) -> SnapshotArtifact:
    state, diagnostics, bundle, categories = synthesize_young_adult_state(
        spec, seed=seed, marginal_path=marginal_path, demo_mode=demo_mode
    )
    age = np.asarray(state["age"], dtype=np.int64)
    household_ids = form_households(age, np.random.default_rng(seed + 1))
    edges = watts_strogatz(spec.count, k=4, beta=0.1, rng=np.random.default_rng(seed + 2))
    agents = [
        {
            "agent_id": f"{spec.population_id}-{index}",
            "household_id": int(household_ids[index]),
            "age_band": str(categories["age_band"][index]),
            "education": str(categories["education"][index]),
            "geography": str(categories["geography"][index]),
            "household_type": str(categories["household_type"][index]),
            "income_band": str(categories["income_band"][index]),
            "occupation_group": str(categories["occupation_group"][index]),
            **{field: state[field][index] for field in STATE_FIELDS},
        }
        for index in range(spec.count)
    ]
    networks = [
        {"source": int(source), "target": int(target), "kind": "small_world"}
        for source, target in edges.tolist()
    ]
    fidelity = {
        "calibration": diagnostics,
        "network": {
            "edge_count": float(edges.shape[0]),
            "mean_degree": float((2 * edges.shape[0]) / spec.count),
        },
    }
    dataset_reference = {
        "canonical_dataset_name": "features.us_young_adult_population_marginals",
        "version": bundle.dataset_reference.get("version", "unversioned"),
        "content_hash": bundle.content_hash,
    }
    return write_snapshot(
        store=SynthStore(output_url),
        spec=spec,
        pack_version=pack_version,
        seed=seed,
        data_versions={
            "features.us_young_adult_population_marginals": bundle.content_hash,
        },
        agents=agents,
        networks=networks,
        institutions=[{"institution_id": "household", "count": int(np.max(household_ids) + 1)}],
        fidelity=fidelity,
        manifest_metadata={
            "dataset_references": [dataset_reference, *bundle.source_references],
            "provenance_manifest": {
                "marginal_bundle_path": str(bundle.path),
                "demo_mode": demo_mode,
                "source_references": bundle.source_references,
            },
            "calibration_diagnostics": diagnostics,
            "imputation": {
                "status": "documented_priors",
                "priors": bundle.priors,
                "default_prior": {"mean": 0.55, "std": 0.16},
                "fields": list(PRIOR_FILLED_FIELDS),
            },
        },
    )
