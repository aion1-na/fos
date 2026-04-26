from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from fos_pack_flourishing.transitions.income import vectorized_income
from fos_pack_flourishing.transitions.social_ties import vectorized_social_ties
from fos_pack_toy_sir.pack import vectorized_infection, vectorized_recovery

ROOT = Path(__file__).resolve().parents[2]
BUDGETS_PATH = ROOT / "docs" / "perf" / "budgets.yml"
AGENTS = 5_000
ITERATIONS = 8

Transition = Callable[[dict[str, np.ndarray], np.random.Generator, dict[str, object], int], dict[str, Any]]


def _load_budgets(path: Path) -> dict[str, float]:
    budgets: dict[str, float] = {}
    in_budget_block = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        if line == "budgets:":
            in_budget_block = True
            continue
        if not in_budget_block or ":" not in line:
            continue
        key, value = line.strip().split(":", 1)
        budgets[key.strip()] = float(value.strip())
    if not budgets:
        raise ValueError(f"no budgets found in {path}")
    return budgets


def _toy_fields() -> dict[str, np.ndarray]:
    status = np.full(AGENTS, "S", dtype="<U1")
    status[:250] = "I"
    return {
        "status": status,
        "days_since_infection": np.arange(AGENTS, dtype=np.int16) % 12,
        "age": 18 + (np.arange(AGENTS, dtype=np.int16) % 45),
    }


def _flourishing_fields() -> dict[str, np.ndarray]:
    base = np.linspace(0.05, 0.95, AGENTS, dtype=np.float64)
    return {
        "income_percentile": base,
        "debt_burden": 1.0 - base,
        "savings_buffer_months": base * 12.0,
        "job_security": np.roll(base, 17),
        "financial": np.roll(base, 31),
        "social_contact_frequency": np.roll(base, 2),
        "trusted_friend_count": np.arange(AGENTS, dtype=np.float64) % 8.0,
        "family_contact": np.roll(base, 5),
        "community_participation": np.roll(base, 13),
        "partner_support": np.roll(base, 29),
        "relationship_quality": np.roll(base, 3),
        "network_support": np.roll(base, 7),
        "loneliness_risk": 1.0 - np.roll(base, 11),
        "caregiving_hours": np.roll(base, 19) * 20.0,
        "relationships": np.roll(base, 23),
    }


def _measure(name: str, transition: Transition, fields: dict[str, np.ndarray]) -> dict[str, float | str]:
    rng = np.random.default_rng(20260426)
    parameters: dict[str, object] = {}
    started = time.perf_counter()
    for tick in range(ITERATIONS):
        result = transition(fields, rng, parameters, tick)
        for field, value in result.get("fields", {}).items():
            fields[field] = np.asarray(value)
    elapsed = time.perf_counter() - started
    per_agent_step = elapsed / (AGENTS * ITERATIONS)
    return {
        "name": name,
        "seconds": round(elapsed, 8),
        "agents": AGENTS,
        "iterations": ITERATIONS,
        "per_agent_step_seconds": per_agent_step,
    }


def main() -> int:
    budgets = _load_budgets(BUDGETS_PATH)
    measurements = [
        _measure("toy_sir_infection", vectorized_infection, _toy_fields()),
        _measure("toy_sir_recovery", vectorized_recovery, _toy_fields()),
        _measure("flourishing_income", vectorized_income, _flourishing_fields()),
        _measure("flourishing_social_ties", vectorized_social_ties, _flourishing_fields()),
    ]
    failures: list[str] = []
    for measurement in measurements:
        name = str(measurement["name"])
        budget = budgets[name]
        actual = float(measurement["per_agent_step_seconds"])
        measurement["budget_seconds"] = budget
        measurement["status"] = "pass" if actual <= budget else "fail"
        if actual > budget:
            failures.append(f"{name}: {actual:.9f}s > {budget:.9f}s per agent-step")

    print(json.dumps({"measurements": measurements}, indent=2, sort_keys=True))
    if failures:
        print("Performance budget exceeded:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
