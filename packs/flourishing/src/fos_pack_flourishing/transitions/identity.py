from __future__ import annotations

from typing import Any

import numpy as np

from fos_pack_flourishing.transitions.common import (
    all_mask,
    annotate_transition,
    clamp,
    require_fields,
)

DEPENDENCIES = ["autonomy_at_work", "skill_match", "education_years", "resilience"]
FIELDS_WRITTEN = ["character"]
EVIDENCE_CLAIMS = ["identity-agency-001"]
COMPOSITION_RULE = "replace"


def vectorized_identity(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, Any]:
    del rng, tick
    require_fields(fields, DEPENDENCIES)
    identity_support = float(parameters.get("identity_support", 0.0))
    education = clamp(fields["education_years"] / 20.0)
    target = (
        0.30 * clamp(fields["autonomy_at_work"])
        + 0.28 * clamp(fields["skill_match"])
        + 0.22 * education
        + 0.20 * clamp(fields["resilience"])
        + identity_support
    )
    next_character = clamp(0.90 * fields["character"] + 0.10 * target)
    return {
        "mode": "replace",
        "fields": {"character": next_character},
        "masks": {"character": all_mask(fields)},
        "kpis": {"mean_character": float(np.mean(next_character))},
    }


annotate_transition(
    vectorized_identity,
    dependencies=DEPENDENCIES,
    fields_written=FIELDS_WRITTEN,
    evidence_claims=EVIDENCE_CLAIMS,
    composition_rule=COMPOSITION_RULE,
)
