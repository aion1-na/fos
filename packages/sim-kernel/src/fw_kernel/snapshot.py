from __future__ import annotations

from fw_kernel.state import ColumnarState


def take_snapshot(state: ColumnarState) -> ColumnarState:
    return state.copy()
