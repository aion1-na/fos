from __future__ import annotations

from fw_contracts import Intervention

MENTORING = Intervention(
    id="mentoring",
    label="Mentoring",
    parameters={
        "eligible_age_min": 16,
        "mentoring_relationship_boost": 0.035,
        "mentoring_purpose_boost": 0.035,
    },
)
