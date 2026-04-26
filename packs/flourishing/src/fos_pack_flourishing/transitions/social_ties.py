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
    "social_contact_frequency",
    "trusted_friend_count",
    "family_contact",
    "community_participation",
    "partner_support",
]
FIELDS_WRITTEN = ["relationships", "loneliness_risk"]
EVIDENCE_CLAIMS = ["social-support-001"]
COMPOSITION_RULE = "replace"


def vectorized_social_ties(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, Any]:
    del rng, tick
    require_fields(fields, DEPENDENCIES)
    mentoring_boost = float(parameters.get("mentoring_relationship_boost", 0.0))
    trusted = clamp(fields["trusted_friend_count"] / 8.0)
    support = (
        0.28 * clamp(fields["social_contact_frequency"])
        + 0.24 * trusted
        + 0.18 * clamp(fields["family_contact"])
        + 0.16 * clamp(fields["community_participation"])
        + 0.14 * clamp(fields["partner_support"])
        + mentoring_boost
    )
    next_relationships = clamp(0.88 * fields["relationships"] + 0.12 * support)
    next_loneliness = clamp(0.92 * fields["loneliness_risk"] + 0.08 * (1.0 - support))
    mask = all_mask(fields)
    return {
        "mode": "replace",
        "fields": {
            "relationships": next_relationships,
            "loneliness_risk": next_loneliness,
        },
        "masks": {"relationships": mask, "loneliness_risk": mask},
        "kpis": {"mean_relationships": float(np.mean(next_relationships))},
    }


annotate_transition(
    vectorized_social_ties,
    dependencies=DEPENDENCIES,
    fields_written=FIELDS_WRITTEN,
    evidence_claims=EVIDENCE_CLAIMS,
    composition_rule=COMPOSITION_RULE,
)
