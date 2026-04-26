from __future__ import annotations

import numpy as np


def increment_value(
    fields: dict[str, np.ndarray],
    rng: np.random.Generator,
    parameters: dict[str, object],
    tick: int,
) -> dict[str, object]:
    del rng, tick
    amount = int(parameters.get("amount", 1))
    value = fields["value"]
    mask = np.ones(value.shape[0], dtype=bool)
    next_value = value + amount
    return {
        "mode": "replace",
        "fields": {"value": next_value},
        "masks": {"value": mask},
        "kpis": {"mean_value": float(np.mean(next_value))},
    }
