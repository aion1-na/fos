from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from fw_contracts import SpawnSpec
from fw_synth.copula import JointConstraint, gaussian_copula_sample
from fw_synth.errors import PopulationSynthError
from fw_synth.fidelity import ks_distance, status_for, wasserstein_distance
from fw_synth.ipf import rake
from fw_synth.networks.household import form_households
from fw_synth.networks.small_world import watts_strogatz
from fw_synth.pipeline import synthesize_snapshot
from fw_synth.snapshot import read_bytes
from fw_synth.store import SynthStore

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "fixtures" / "gfs_us_18_24.parquet"


def test_ipf_matches_marginals() -> None:
    weights = np.ones(4)
    result = rake(
        weights,
        dimensions={
            "age_band": np.asarray(["18-20", "18-20", "21-24", "21-24"]),
            "group": np.asarray(["a", "b", "a", "b"]),
        },
        targets={
            "age_band": {"18-20": 3.0, "21-24": 1.0},
            "group": {"a": 2.0, "b": 2.0},
        },
    )

    assert result.max_error <= 1e-8
    assert result.weights.sum() == pytest.approx(4.0)


def test_ipf_non_convergence_raises_typed_error() -> None:
    with pytest.raises(PopulationSynthError):
        rake(
            np.asarray([1.0]),
            dimensions={"x": np.asarray(["a"])},
            targets={"x": {"a": 2.0}},
            threshold=0.0,
            max_iterations=1,
        )


def test_gaussian_copula_is_deterministic() -> None:
    constraints = [
        JointConstraint("x", mean=0.0, std=1.0),
        JointConstraint("y", mean=2.0, std=0.5),
    ]
    corr = np.asarray([[1.0, 0.25], [0.25, 1.0]])

    first = gaussian_copula_sample(8, constraints, corr, np.random.default_rng(7))
    second = gaussian_copula_sample(8, constraints, corr, np.random.default_rng(7))

    assert np.array_equal(first["x"], second["x"])
    assert np.array_equal(first["y_u"], second["y_u"])


def test_network_generators_are_deterministic() -> None:
    first_edges = watts_strogatz(20, k=4, beta=0.2, rng=np.random.default_rng(4))
    second_edges = watts_strogatz(20, k=4, beta=0.2, rng=np.random.default_rng(4))
    first_households = form_households(np.arange(20), rng=np.random.default_rng(5))
    second_households = form_households(np.arange(20), rng=np.random.default_rng(5))

    assert np.array_equal(first_edges, second_edges)
    assert np.array_equal(first_households, second_households)


def test_fidelity_metrics_and_status() -> None:
    left = np.asarray([1, 2, 3])
    right = np.asarray([1, 2, 4])

    assert ks_distance(left, right) >= 0
    assert wasserstein_distance(left, right) == pytest.approx(1 / 3)
    assert status_for(0.01, {"green": 0.02, "amber": 0.05}) == "green"
    assert status_for(0.03, {"green": 0.02, "amber": 0.05}) == "amber"
    assert status_for(0.06, {"green": 0.02, "amber": 0.05}) == "red"


def test_fixture_young_adult_population_green(tmp_path: Path) -> None:
    spec = SpawnSpec(
        population_id="young-adult",
        count=5000,
        state_seed={"initial_infected": 25},
    )
    artifact = synthesize_snapshot(
        spec=spec,
        pack_version="0.1.0",
        seed=11,
        output_url=str(tmp_path),
        reference_path=str(FIXTURE),
        data_versions={"reference": "fixture-v1"},
    )

    assert artifact.snapshot.id == artifact.manifest["snapshot_id"]
    assert artifact.manifest["spawn_spec"]["count"] == 5000
    assert artifact.manifest["data_versions"] == {"reference": "fixture-v1"}
    assert artifact.path.endswith(artifact.snapshot.id)
    fidelity = artifact.manifest
    stored = read_bytes(SynthStore(str(tmp_path)), artifact.path)
    assert b"young-adult" in stored["manifest.json"]
    assert fidelity["snapshot_id"] == artifact.snapshot.id

    table = pq.read_table(f"{artifact.path}/agents.parquet")
    assert table.num_rows == 5000
    assert set(table.column_names) >= {
        "agent_id",
        "age",
        "status",
        "days_since_infection",
        "household_id",
    }
    fidelity_data = (Path(artifact.path) / "fidelity.json").read_text(encoding="utf-8")
    assert '"status":"green"' in fidelity_data


def test_snapshot_id_and_parquet_are_byte_identical_across_processes(tmp_path: Path) -> None:
    script = f"""
from pathlib import Path
from fw_contracts import SpawnSpec
from fw_synth.pipeline import synthesize_snapshot

output = Path({str(tmp_path)!r})
spec = SpawnSpec(
    population_id="deterministic",
    count=5000,
    state_seed={{"initial_infected": 25}},
)
artifact = synthesize_snapshot(
    spec=spec,
    pack_version="0.1.0",
    seed=19,
    output_url=str(output),
    reference_path={str(FIXTURE)!r},
    data_versions={{"reference": "fixture-v1"}},
)
print(artifact.path)
"""
    first_path = Path(
        subprocess.check_output([sys.executable, "-c", script], text=True).strip()
    )
    first_bytes = (first_path / "agents.parquet").read_bytes()
    second_path = Path(
        subprocess.check_output([sys.executable, "-c", script], text=True).strip()
    )
    second_bytes = (second_path / "agents.parquet").read_bytes()

    assert first_path == second_path
    assert first_bytes == second_bytes


def test_fixture_exists() -> None:
    table = pq.read_table(FIXTURE)

    assert table.num_rows == 5000
    assert table.schema == pa.schema([("age", pa.int64())])


def test_cli_synthesize_and_fidelity(tmp_path: Path) -> None:
    spec_path = ROOT / "fixtures" / "young_adult_spec.yml"
    first = tmp_path / "snap1"
    second = tmp_path / "snap2"

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "fw_synth.cli",
            "synthesize",
            "--spec",
            str(spec_path),
            "--out",
            str(first),
        ]
    )
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "fw_synth.cli",
            "synthesize",
            "--spec",
            str(spec_path),
            "--out",
            str(second),
        ]
    )
    first_file = next(first.glob("*/agents.parquet"))
    second_file = next(second.glob("*/agents.parquet"))
    assert first_file.read_bytes() == second_file.read_bytes()

    output = subprocess.check_output(
        [
            sys.executable,
            "-m",
            "fw_synth.cli",
            "fidelity",
            "--snapshot",
            str(first),
        ],
        text=True,
    )
    assert '"status": "green"' in output
