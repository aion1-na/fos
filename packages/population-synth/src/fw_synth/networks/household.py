from __future__ import annotations

import numpy as np


def form_households(
    ages: np.ndarray,
    rng: np.random.Generator,
    min_size: int = 1,
    max_size: int = 4,
) -> np.ndarray:
    if min_size <= 0 or max_size < min_size:
        raise ValueError("invalid household size range")
    count = int(np.asarray(ages).shape[0])
    order = np.argsort(np.asarray(ages), kind="stable")
    household_ids = np.empty(count, dtype=np.int64)
    cursor = 0
    household_id = 0
    while cursor < count:
        size = int(rng.integers(min_size, max_size + 1))
        members = order[cursor : min(cursor + size, count)]
        household_ids[members] = household_id
        household_id += 1
        cursor += size
    return household_ids
