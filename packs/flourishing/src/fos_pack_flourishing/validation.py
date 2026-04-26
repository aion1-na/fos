from __future__ import annotations

from typing import Any

import numpy as np


def backtest_against_heldout_wave(
    predicted: dict[str, np.ndarray],
    heldout: dict[str, np.ndarray],
    *,
    fields: list[str],
) -> dict[str, float]:
    return {
        field: float(np.mean((predicted[field].astype(float) - heldout[field].astype(float)) ** 2))
        for field in fields
    }


def e_value(risk_ratio: float) -> float:
    if risk_ratio < 1.0:
        risk_ratio = 1.0 / risk_ratio
    return float(risk_ratio + np.sqrt(risk_ratio * (risk_ratio - 1.0)))


def drift_check(
    baseline: dict[str, np.ndarray],
    current: dict[str, np.ndarray],
    *,
    fields: list[str],
    threshold: float = 0.10,
) -> dict[str, Any]:
    metrics = {
        field: float(abs(np.mean(current[field].astype(float)) - np.mean(baseline[field].astype(float))))
        for field in fields
    }
    return {
        "passed": all(value <= threshold for value in metrics.values()),
        "threshold": threshold,
        "metrics": metrics,
    }


def run_validation() -> dict[str, Any]:
    baseline = {
        "happiness": np.asarray([0.50, 0.60, 0.70]),
        "health": np.asarray([0.55, 0.62, 0.72]),
        "meaning": np.asarray([0.51, 0.59, 0.69]),
    }
    heldout = {
        "happiness": np.asarray([0.52, 0.61, 0.69]),
        "health": np.asarray([0.56, 0.61, 0.70]),
        "meaning": np.asarray([0.53, 0.60, 0.68]),
    }
    fields = ["happiness", "health", "meaning"]
    backtest = backtest_against_heldout_wave(baseline, heldout, fields=fields)
    drift = drift_check(baseline, heldout, fields=fields, threshold=0.05)
    return {
        "passed": max(backtest.values()) < 0.01 and bool(drift["passed"]),
        "backtest_mse": backtest,
        "e_value": e_value(1.4),
        "drift": drift,
    }
