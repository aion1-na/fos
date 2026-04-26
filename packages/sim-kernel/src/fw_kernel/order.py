from __future__ import annotations

from fw_contracts import TransitionModel


def deterministic_order(transitions: list[TransitionModel]) -> list[TransitionModel]:
    return list(transitions)
