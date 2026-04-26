from __future__ import annotations

from dataclasses import dataclass
from statistics import NormalDist
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class JointConstraint:
    name: str
    mean: float
    std: float


def _normal_cdf(values: np.ndarray) -> np.ndarray:
    normal = NormalDist()
    return np.asarray([normal.cdf(float(value)) for value in values], dtype=float)


def gaussian_copula_sample(
    count: int,
    constraints: Sequence[JointConstraint],
    correlation: np.ndarray,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    if count < 0:
        raise ValueError("count must be non-negative")
    if not constraints:
        return {}
    corr = np.asarray(correlation, dtype=float)
    width = len(constraints)
    if corr.shape != (width, width):
        raise ValueError("correlation matrix shape does not match constraints")

    normals = rng.multivariate_normal(np.zeros(width), corr, size=count)
    samples: dict[str, np.ndarray] = {}
    for index, constraint in enumerate(constraints):
        uniform = _normal_cdf(normals[:, index])
        samples[constraint.name] = constraint.mean + constraint.std * normals[:, index]
        samples[f"{constraint.name}_u"] = uniform
    return samples
