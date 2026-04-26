from __future__ import annotations

from importlib import import_module
from typing import Any, Callable

import numpy as np
from fw_contracts import TransitionModel

from fw_kernel.state import ColumnarState
from fw_kernel.types import RuntimeContext, TransitionPatch


def _load_entrypoint(path: str) -> Callable[..., dict[str, Any]]:
    module_name, function_name = path.rsplit(".", 1)
    module = import_module(module_name)
    function = getattr(module, function_name)
    if not callable(function):
        raise TypeError(f"transition entrypoint is not callable: {path}")
    return function


def _normalize_patch(
    transition: TransitionModel,
    raw_patch: dict[str, Any],
    state: ColumnarState,
) -> TransitionPatch:
    mode = str(raw_patch.get("mode", "replace"))
    raw_fields = raw_patch.get("fields", {})
    if not isinstance(raw_fields, dict):
        raise TypeError("transition patch fields must be an object")
    fields = {name: np.asarray(values) for name, values in raw_fields.items()}
    for name, values in fields.items():
        if values.shape[0] != state.size:
            raise ValueError(
                f"transition {transition.id!r} field {name!r} returned wrong size"
            )
    raw_masks = raw_patch.get("masks", {})
    if not isinstance(raw_masks, dict):
        raise TypeError("transition patch masks must be an object")
    masks = {name: np.asarray(values, dtype=bool) for name, values in raw_masks.items()}
    for name in fields:
        if name not in masks:
            masks[name] = np.ones(state.size, dtype=bool)
    for name, mask in masks.items():
        if mask.shape[0] != state.size:
            raise ValueError(
                f"transition {transition.id!r} mask {name!r} returned wrong size"
            )
    raw_kpis = raw_patch.get("kpis", {})
    if not isinstance(raw_kpis, dict):
        raise TypeError("transition patch kpis must be an object")
    kpis = {str(name): float(value) for name, value in raw_kpis.items()}
    return TransitionPatch(
        transition_id=transition.id,
        mode=mode,
        fields=fields,
        masks=masks,
        kpis=kpis,
    )


def compute_transition(
    transition: TransitionModel,
    snapshot: ColumnarState,
    rng: np.random.Generator,
    context: RuntimeContext,
) -> TransitionPatch:
    function = _load_entrypoint(transition.entrypoint)
    raw_patch = function(
        snapshot.fields,
        rng=rng,
        parameters=context.scenario_parameters,
        tick=context.tick,
    )
    if not isinstance(raw_patch, dict):
        raise TypeError(f"transition {transition.id!r} must return an object patch")
    return _normalize_patch(transition, raw_patch, snapshot)
