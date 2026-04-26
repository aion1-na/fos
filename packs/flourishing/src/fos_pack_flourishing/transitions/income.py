from __future__ import annotations

from typing import Any

import numpy as np

from fos_pack_flourishing.transitions.common import (
    all_mask,
    annotate_transition,
    clamp,
    require_fields,
)

DEPENDENCIES = ["income_percentile", "debt_burden", "savings_buffer_months", "job_security"]
FIELDS_WRITTEN = ["financial"]
EVIDENCE_CLAIMS = ["income-security-001"]
COMPOSITION_RULE = "replace"


def vectorized_income(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, Any]:
    del rng
    require_fields(fields, DEPENDENCIES)
    policy_boost = float(parameters.get("income_policy_boost", 0.0))
    savings = clamp(fields["savings_buffer_months"] / 12.0)
    target = (
        0.42 * clamp(fields["income_percentile"])
        + 0.22 * (1.0 - clamp(fields["debt_burden"]))
        + 0.18 * savings
        + 0.18 * clamp(fields["job_security"])
        + policy_boost
    )
    drift = min(0.18, 0.05 + tick * 0.001)
    next_financial = clamp((1.0 - drift) * fields["financial"] + drift * target)
    mask = all_mask(fields)
    return {
        "mode": "replace",
        "fields": {"financial": next_financial},
        "masks": {"financial": mask},
        "kpis": {"mean_financial": float(np.mean(next_financial))},
    }


annotate_transition(
    vectorized_income,
    dependencies=DEPENDENCIES,
    fields_written=FIELDS_WRITTEN,
    evidence_claims=EVIDENCE_CLAIMS,
    composition_rule=COMPOSITION_RULE,
)
