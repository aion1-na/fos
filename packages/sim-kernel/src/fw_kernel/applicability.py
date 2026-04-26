from __future__ import annotations

from fw_contracts import TransitionModel


def applicable_transitions(
    transitions: list[TransitionModel],
    enabled_transition_ids: list[str] | None,
) -> list[TransitionModel]:
    if enabled_transition_ids is None:
        return list(transitions)
    enabled = {transition_id: index for index, transition_id in enumerate(enabled_transition_ids)}
    return [transition for transition in transitions if transition.id in enabled]
