from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from fw_contracts import Population


@dataclass
class ColumnarState:
    agent_ids: np.ndarray
    fields: dict[str, np.ndarray]

    @property
    def size(self) -> int:
        return int(self.agent_ids.shape[0])

    def copy(self) -> ColumnarState:
        return ColumnarState(
            agent_ids=self.agent_ids.copy(),
            fields={name: values.copy() for name, values in self.fields.items()},
        )


def state_from_population(population: Population) -> ColumnarState:
    raw_state = population.metadata.get("state", {})
    if not isinstance(raw_state, dict):
        raise TypeError("population.metadata['state'] must be an object")
    agent_ids = (
        np.asarray(population.agent_ids, dtype=str)
        if population.agent_ids
        else np.asarray(
            [f"{population.id}-{index}" for index in range(population.size)], dtype=str
        )
    )
    fields: dict[str, np.ndarray] = {}
    for name, values in raw_state.items():
        array = np.asarray(values)
        if array.shape[0] != agent_ids.shape[0]:
            raise ValueError(f"state field {name!r} does not match population size")
        fields[name] = array.copy()
    return ColumnarState(agent_ids=agent_ids, fields=fields)


def state_to_jsonable(state: ColumnarState) -> dict[str, Any]:
    return {
        "agent_ids": state.agent_ids.tolist(),
        "fields": {name: values.tolist() for name, values in sorted(state.fields.items())},
    }
