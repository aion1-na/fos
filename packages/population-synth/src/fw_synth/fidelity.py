from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FidelityMetric:
    name: str
    value: float
    status: str


def ks_distance(left: np.ndarray, right: np.ndarray) -> float:
    a = np.sort(np.asarray(left, dtype=float))
    b = np.sort(np.asarray(right, dtype=float))
    values = np.sort(np.concatenate([a, b]))
    cdf_a = np.searchsorted(a, values, side="right") / max(1, a.shape[0])
    cdf_b = np.searchsorted(b, values, side="right") / max(1, b.shape[0])
    return float(np.max(np.abs(cdf_a - cdf_b))) if values.shape[0] else 0.0


def wasserstein_distance(left: np.ndarray, right: np.ndarray) -> float:
    a = np.sort(np.asarray(left, dtype=float))
    b = np.sort(np.asarray(right, dtype=float))
    width = min(a.shape[0], b.shape[0])
    if width == 0:
        return 0.0
    return float(np.mean(np.abs(a[:width] - b[:width])))


def network_diagnostics(edges: np.ndarray, node_count: int) -> dict[str, float]:
    if node_count <= 0:
        return {"mean_degree": 0.0, "edge_count": 0.0}
    edge_count = int(np.asarray(edges).shape[0])
    return {
        "edge_count": float(edge_count),
        "mean_degree": float((2 * edge_count) / node_count),
    }


def status_for(value: float, thresholds: dict[str, float]) -> str:
    green = float(thresholds.get("green", 0.05))
    amber = float(thresholds.get("amber", 0.1))
    if value <= green:
        return "green"
    if value <= amber:
        return "amber"
    return "red"


def attribute_report(
    reference: dict[str, np.ndarray],
    synthetic: dict[str, np.ndarray],
    thresholds: dict[str, dict[str, float]],
) -> dict[str, dict[str, float | str]]:
    report: dict[str, dict[str, float | str]] = {}
    for name in sorted(reference):
        metric_value = ks_distance(reference[name], synthetic[name])
        report[name] = {
            "ks": metric_value,
            "status": status_for(metric_value, thresholds.get(name, {})),
        }
    return report
