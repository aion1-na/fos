from __future__ import annotations

from fw_contracts import Intervention

JOB_TRAINING = Intervention(
    id="job-training",
    label="Job training",
    parameters={
        "eligible_age_min": 18,
        "skill_match_boost": 0.05,
        "income_policy_boost": 0.03,
    },
)
