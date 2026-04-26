from __future__ import annotations

import numpy as np


def watts_strogatz(
    count: int,
    k: int,
    beta: float,
    rng: np.random.Generator,
) -> np.ndarray:
    if count < 0:
        raise ValueError("count must be non-negative")
    if k <= 0 or k >= count:
        raise ValueError("k must be positive and smaller than count")
    if k % 2:
        raise ValueError("k must be even")
    if beta < 0 or beta > 1:
        raise ValueError("beta must be between 0 and 1")

    edges: list[tuple[int, int]] = []
    half = k // 2
    adjacency = np.zeros((count, count), dtype=bool)
    for source in range(count):
        for offset in range(1, half + 1):
            target = (source + offset) % count
            adjacency[source, target] = True
            adjacency[target, source] = True

    for source in range(count):
        for offset in range(1, half + 1):
            target = (source + offset) % count
            if rng.random() >= beta:
                continue
            adjacency[source, target] = False
            adjacency[target, source] = False
            candidates = np.flatnonzero(~adjacency[source])
            candidates = candidates[candidates != source]
            replacement = int(candidates[int(rng.integers(0, candidates.shape[0]))])
            adjacency[source, replacement] = True
            adjacency[replacement, source] = True

    rows, cols = np.where(np.triu(adjacency, k=1))
    for source, target in zip(rows.tolist(), cols.tolist(), strict=True):
        edges.append((source, target))
    return np.asarray(edges, dtype=np.int64)
