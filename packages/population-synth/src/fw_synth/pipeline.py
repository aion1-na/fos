from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.parquet as pq
from fw_contracts import SpawnSpec

from fw_synth.fidelity import attribute_report, network_diagnostics
from fw_synth.networks.household import form_households
from fw_synth.networks.small_world import watts_strogatz
from fw_synth.snapshot import SnapshotArtifact, write_snapshot
from fw_synth.store import SynthStore


def _reference_columns(reference_path: str | None) -> dict[str, np.ndarray]:
    if reference_path is None:
        return {}
    table = pq.read_table(reference_path)
    return {name: table[name].to_numpy() for name in table.column_names}


def synthesize_state(
    spec: SpawnSpec,
    seed: int,
    reference_path: str | None = None,
) -> dict[str, list[int] | list[str]]:
    rng = np.random.default_rng(seed)
    reference = _reference_columns(reference_path)
    count = spec.count

    if "age" in reference and reference["age"].shape[0] >= count:
        age = np.sort(reference["age"][:count].astype(np.int64), kind="stable")
    elif "age" in reference:
        indexes = rng.integers(0, reference["age"].shape[0], size=count)
        age = reference["age"][indexes].astype(np.int64)
    else:
        adult_share = float(spec.state_seed.get("adult_share", 0.8))
        adult_cutoff = round(count * adult_share)
        age = np.empty(count, dtype=np.int64)
        age[:adult_cutoff] = 35
        age[adult_cutoff:] = 12

    initial_infected = int(spec.state_seed.get("initial_infected", 10))
    if initial_infected < 0 or initial_infected > count:
        raise ValueError("initial_infected must be between 0 and count")
    status = np.full(count, "S", dtype="<U1")
    status[:initial_infected] = "I"
    days = np.zeros(count, dtype=np.int64)
    days[:initial_infected] = 1
    return {
        "status": status.tolist(),
        "days_since_infection": days.tolist(),
        "age": age.tolist(),
    }


def synthesize_snapshot(
    spec: SpawnSpec,
    pack_version: str,
    seed: int,
    output_url: str,
    reference_path: str | None = None,
    data_versions: dict[str, str] | None = None,
    thresholds: dict[str, dict[str, float]] | None = None,
) -> SnapshotArtifact:
    state = synthesize_state(spec, seed=seed, reference_path=reference_path)
    age = np.asarray(state["age"], dtype=np.int64)
    household_ids = form_households(age, np.random.default_rng(seed + 1))
    edges = watts_strogatz(spec.count, k=4, beta=0.1, rng=np.random.default_rng(seed + 2))
    reference = _reference_columns(reference_path)
    thresholds = thresholds or {"age": {"green": 0.01, "amber": 0.05}}

    agents = [
        {
            "agent_id": f"{spec.population_id}-{index}",
            "age": int(age[index]),
            "status": str(state["status"][index]),
            "days_since_infection": int(state["days_since_infection"][index]),
            "household_id": int(household_ids[index]),
        }
        for index in range(spec.count)
    ]
    networks = [
        {"source": int(source), "target": int(target), "kind": "small_world"}
        for source, target in edges.tolist()
    ]
    institutions: list[dict[str, Any]] = [
        {"institution_id": "household", "count": int(np.max(household_ids) + 1)}
    ]
    fidelity = {
        "attributes": attribute_report(
            {"age": reference["age"][: spec.count]} if "age" in reference else {"age": age},
            {"age": age},
            thresholds,
        ),
        "network": network_diagnostics(edges, spec.count),
    }
    data_versions = data_versions or {
        "reference": (
            Path(reference_path).name if reference_path is not None else "synthetic-default"
        )
    }
    return write_snapshot(
        store=SynthStore(output_url),
        spec=spec,
        pack_version=pack_version,
        seed=seed,
        data_versions=data_versions,
        agents=agents,
        networks=networks,
        institutions=institutions,
        fidelity=fidelity,
    )
