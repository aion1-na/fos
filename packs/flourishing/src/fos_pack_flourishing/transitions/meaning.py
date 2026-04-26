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
    "purpose_clarity",
    "values_alignment",
    "volunteering_hours",
    "learning_hours",
    "creative_hours",
]
FIELDS_WRITTEN = ["meaning"]
EVIDENCE_CLAIMS = ["meaning-purpose-001"]
COMPOSITION_RULE = "replace"


def vectorized_meaning(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, Any]:
    del rng, tick
    require_fields(fields, DEPENDENCIES)
    mentoring_boost = float(parameters.get("mentoring_purpose_boost", 0.0))
    contribution = clamp(fields["volunteering_hours"] / 12.0)
    learning = clamp(fields["learning_hours"] / 10.0)
    creative = clamp(fields["creative_hours"] / 8.0)
    target = (
        0.32 * clamp(fields["purpose_clarity"])
        + 0.28 * clamp(fields["values_alignment"])
        + 0.16 * contribution
        + 0.13 * learning
        + 0.11 * creative
        + mentoring_boost
    )
    next_meaning = clamp(0.90 * fields["meaning"] + 0.10 * target)
    return {
        "mode": "replace",
        "fields": {"meaning": next_meaning},
        "masks": {"meaning": all_mask(fields)},
        "kpis": {"mean_meaning": float(np.mean(next_meaning))},
    }


annotate_transition(
    vectorized_meaning,
    dependencies=DEPENDENCIES,
    fields_written=FIELDS_WRITTEN,
    evidence_claims=EVIDENCE_CLAIMS,
    composition_rule=COMPOSITION_RULE,
)
