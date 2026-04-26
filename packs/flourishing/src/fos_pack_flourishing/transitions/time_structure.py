from __future__ import annotations

from typing import Any

import numpy as np

from fos_pack_flourishing.transitions.common import (
    all_mask,
    annotate_transition,
    clamp,
    require_fields,
)

DEPENDENCIES = ["work_hours", "care_hours", "sleep_hours", "schedule_volatility"]
FIELDS_WRITTEN = ["happiness"]
EVIDENCE_CLAIMS = ["time-structure-001"]
COMPOSITION_RULE = "replace"


def vectorized_time_structure(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, Any]:
    del rng, tick
    require_fields(fields, DEPENDENCIES)
    leave_boost = float(parameters.get("paid_leave_time_boost", 0.0))
    work_balance = 1.0 - np.abs(fields["work_hours"] - 38.0) / 62.0
    care_balance = 1.0 - clamp(fields["care_hours"] / 80.0)
    sleep_balance = 1.0 - np.abs(fields["sleep_hours"] - 7.5) / 7.5
    target = (
        0.32 * clamp(work_balance)
        + 0.22 * clamp(care_balance)
        + 0.24 * clamp(sleep_balance)
        + 0.22 * (1.0 - clamp(fields["schedule_volatility"]))
        + leave_boost
    )
    next_happiness = clamp(0.89 * fields["happiness"] + 0.11 * target)
    return {
        "mode": "replace",
        "fields": {"happiness": next_happiness},
        "masks": {"happiness": all_mask(fields)},
        "kpis": {"mean_happiness": float(np.mean(next_happiness))},
    }


annotate_transition(
    vectorized_time_structure,
    dependencies=DEPENDENCIES,
    fields_written=FIELDS_WRITTEN,
    evidence_claims=EVIDENCE_CLAIMS,
    composition_rule=COMPOSITION_RULE,
)
