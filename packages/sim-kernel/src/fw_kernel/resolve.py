from __future__ import annotations

import numpy as np

from fw_kernel.types import TransitionPatch


def resolve_composition(patches: list[TransitionPatch]) -> TransitionPatch:
    merged_fields: dict[str, np.ndarray] = {}
    merged_masks: dict[str, np.ndarray] = {}
    kpis: dict[str, float] = {}

    for patch in patches:
        if patch.mode != "replace":
            raise ValueError(f"unsupported transition composition mode: {patch.mode}")
        for name, values in patch.fields.items():
            mask = patch.masks[name]
            existing = merged_fields.get(name)
            if existing is None:
                merged_fields[name] = values.copy()
                merged_masks[name] = mask.copy()
                continue
            overlap = merged_masks[name] & mask
            if np.any(overlap) and not np.array_equal(existing[overlap], values[overlap]):
                raise ValueError(f"conflicting replace declarations for field {name!r}")
            write_indexes = mask & ~merged_masks[name]
            existing[write_indexes] = values[write_indexes]
            merged_masks[name] = merged_masks[name] | mask
        for name, value in patch.kpis.items():
            kpis[f"{patch.transition_id}.{name}"] = float(value)

    return TransitionPatch(
        transition_id="resolved",
        mode="replace",
        fields=merged_fields,
        masks=merged_masks,
        kpis=kpis,
    )
