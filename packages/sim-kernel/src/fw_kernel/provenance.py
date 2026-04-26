from __future__ import annotations

import hashlib
import json

from fw_kernel.state import ColumnarState, state_to_jsonable


def tick_hash(tick: int, state: ColumnarState, kpis: dict[str, float]) -> str:
    payload = {
        "tick": tick,
        "state": state_to_jsonable(state),
        "kpis": {name: kpis[name] for name in sorted(kpis)},
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
