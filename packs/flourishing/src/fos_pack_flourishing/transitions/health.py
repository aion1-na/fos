from __future__ import annotations

from typing import Any

import numpy as np

from fos_pack_flourishing.transitions.common import (
    all_mask,
    annotate_transition,
    clamp,
    require_fields,
)

DEPENDENCIES = [
    "sleep_hours",
    "exercise_minutes",
    "preventive_care_access",
    "chronic_condition_count",
    "stress_load",
]
FIELDS_WRITTEN = ["health", "resilience"]
EVIDENCE_CLAIMS = ["health-behavior-001"]
COMPOSITION_RULE = "replace"


def vectorized_health(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, Any]:
    del rng, tick
    require_fields(fields, DEPENDENCIES)
    sleep = 1.0 - np.abs(fields["sleep_hours"] - 7.5) / 7.5
    activity = clamp(fields["exercise_minutes"] / 45.0)
    conditions = 1.0 - clamp(fields["chronic_condition_count"] / 5.0)
    target = (
        0.25 * clamp(sleep)
        + 0.22 * activity
        + 0.24 * clamp(fields["preventive_care_access"])
        + 0.16 * conditions
        + 0.13 * (1.0 - clamp(fields["stress_load"]))
    )
    next_health = clamp(0.91 * fields["health"] + 0.09 * target)
    next_resilience = clamp(
        0.94 * fields["resilience"]
        + 0.06 * (0.45 * next_health + 0.35 * (1.0 - clamp(fields["stress_load"])) + 0.20 * activity)
    )
    mask = all_mask(fields)
    return {
        "mode": "replace",
        "fields": {"health": next_health, "resilience": next_resilience},
        "masks": {"health": mask, "resilience": mask},
        "kpis": {"mean_health": float(np.mean(next_health))},
    }


annotate_transition(
    vectorized_health,
    dependencies=DEPENDENCIES,
    fields_written=FIELDS_WRITTEN,
    evidence_claims=EVIDENCE_CLAIMS,
    composition_rule=COMPOSITION_RULE,
)
