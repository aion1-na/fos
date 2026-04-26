from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from fw_kernel.state import ColumnarState


@dataclass(frozen=True)
class RuntimeContext:
    run_seed: int
    tick: int
    scenario_parameters: dict[str, Any]


@dataclass
class TransitionPatch:
    transition_id: str
    mode: str
    fields: dict[str, np.ndarray] = field(default_factory=dict)
    masks: dict[str, np.ndarray] = field(default_factory=dict)
    kpis: dict[str, float] = field(default_factory=dict)


@dataclass
class TickRecord:
    tick: int
    state: ColumnarState
    kpis: dict[str, float]
    tick_hash: str
