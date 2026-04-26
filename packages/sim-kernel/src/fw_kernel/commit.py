from __future__ import annotations

from fw_kernel.state import ColumnarState
from fw_kernel.types import TransitionPatch


def commit_patch(state: ColumnarState, patch: TransitionPatch) -> ColumnarState:
    next_state = state.copy()
    for name, values in patch.fields.items():
        current = next_state.fields[name].copy()
        mask = patch.masks[name]
        current[mask] = values[mask]
        next_state.fields[name] = current
    return next_state
