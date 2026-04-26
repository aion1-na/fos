from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np


def clamp(values: np.ndarray, low: float = 0.0, high: float = 1.0) -> np.ndarray:
    return np.clip(values.astype(float), low, high)


def require_fields(fields: dict[str, np.ndarray], names: list[str]) -> None:
    missing = [name for name in names if name not in fields]
    if missing:
        raise KeyError(f"missing flourishing state fields: {', '.join(missing)}")


def all_mask(fields: dict[str, np.ndarray]) -> np.ndarray:
    first = next(iter(fields.values()))
    return np.ones(first.shape[0], dtype=bool)


def annotate_transition(
    function: Callable[..., dict[str, Any]],
    *,
    dependencies: list[str],
    fields_written: list[str],
    evidence_claims: list[str],
    applicability_filter: str = "all",
    composition_rule: str = "replace",
) -> Callable[..., dict[str, Any]]:
    function.dependencies = dependencies
    function.applicability_filter = applicability_filter
    function.fields_written = fields_written
    function.composition_rule = composition_rule
    function.evidence_claims = evidence_claims
    function.behavior_model = "deterministic-vectorized"
    return function
