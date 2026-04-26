from __future__ import annotations

from fw_kernel.state import ColumnarState
from fw_kernel.types import TransitionPatch


def propagate_once(state: ColumnarState, patch: TransitionPatch) -> TransitionPatch:
    return patch
