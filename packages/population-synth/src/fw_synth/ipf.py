from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fw_synth.errors import PopulationSynthError


@dataclass(frozen=True)
class IpfResult:
    weights: np.ndarray
    iterations: int
    max_error: float


def rake(
    seed_weights: np.ndarray,
    dimensions: dict[str, np.ndarray],
    targets: dict[str, dict[str, float]],
    threshold: float = 1e-8,
    max_iterations: int = 1_000,
) -> IpfResult:
    weights = np.asarray(seed_weights, dtype=float).copy()
    if weights.ndim != 1:
        raise ValueError("seed_weights must be one-dimensional")
    if np.any(weights < 0):
        raise ValueError("seed_weights must be non-negative")

    encoded_dimensions = {
        name: np.asarray(values, dtype=str) for name, values in dimensions.items()
    }
    for name, values in encoded_dimensions.items():
        if values.shape[0] != weights.shape[0]:
            raise ValueError(f"dimension {name!r} length does not match weights")

    max_error = float("inf")
    for iteration in range(1, max_iterations + 1):
        max_error = 0.0
        for dimension_name in sorted(targets):
            values = encoded_dimensions[dimension_name]
            for category in sorted(targets[dimension_name]):
                target = float(targets[dimension_name][category])
                mask = values == category
                current = float(np.sum(weights[mask]))
                if target == 0:
                    weights[mask] = 0
                    continue
                if current <= 0:
                    raise PopulationSynthError(
                        f"cannot rake {dimension_name!r}/{category!r}: zero support"
                    )
                ratio = target / current
                weights[mask] *= ratio
                max_error = max(max_error, abs(target - current))
        if max_error <= threshold:
            return IpfResult(weights=weights, iterations=iteration, max_error=max_error)

    raise PopulationSynthError(
        f"IPF did not converge within {max_iterations} iterations; max_error={max_error}"
    )
