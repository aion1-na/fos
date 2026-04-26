from __future__ import annotations

from fw_contracts import Intervention

PAID_LEAVE = Intervention(
    id="paid-leave",
    label="Paid leave",
    parameters={
        "eligible_employment_status": ["employed", "caregiver"],
        "paid_leave_time_boost": 0.04,
    },
)
