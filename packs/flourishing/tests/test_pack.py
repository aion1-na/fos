from __future__ import annotations

import importlib
import subprocess
import sys
from pathlib import Path

from fos_pack_flourishing import INTERVENTIONS, build_pack, spawn_population_state
from fos_pack_flourishing.state_schema import STATE_FIELD_COUNT
from fos_pack_flourishing.validation import run_validation
from fw_contracts import SpawnSpec


ROOT = Path(__file__).resolve().parents[3]


def test_pack_uses_domain_pack_contract() -> None:
    pack = build_pack()

    assert pack.id == "flourishing"
    assert pack.contracts_version == "0.1.0"
    assert pack.version == "0.1.0"
    assert len(pack.transition_models) == 6
    assert len(pack.validation_suites) == 1
    assert [intervention.id for intervention in INTERVENTIONS] == [
        "paid-leave",
        "job-training",
        "mentoring",
    ]


def test_state_schema_has_expected_agent_width() -> None:
    pack = build_pack()

    assert 60 <= STATE_FIELD_COUNT <= 80
    assert len(pack.state_schema["properties"]) == STATE_FIELD_COUNT
    assert {"happiness", "health", "meaning", "relationships", "financial"} <= set(
        pack.state_schema["properties"]
    )


def test_spawn_state_is_deterministic_and_complete() -> None:
    spec = SpawnSpec(population_id="flourishing-test", count=12, state_seed={"seed": 44})

    first = spawn_population_state(spec)
    second = spawn_population_state(spec)

    assert first == second
    assert len(first) == STATE_FIELD_COUNT
    assert all(len(values) == spec.count for values in first.values())


def test_transitions_declare_evidence_and_non_llm_behavior() -> None:
    pack = build_pack()
    for transition in pack.transition_models:
        module_name, function_name = transition.entrypoint.rsplit(".", 1)
        function = getattr(importlib.import_module(module_name), function_name)
        assert function.evidence_claims
        assert function.behavior_model == "deterministic-vectorized"
        assert function.composition_rule == "replace"
        assert function.fields_written
        assert function.dependencies


def test_validation_suite_v0_runs() -> None:
    report = run_validation()

    assert report["passed"] is True
    assert report["e_value"] > 1.0


def test_pack_lint_accepts_flourishing_pack() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/lint/pack-lint.py"), str(ROOT / "packs/flourishing")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_pack_lint_rejects_missing_transition_evidence(tmp_path: Path) -> None:
    pack_dir = tmp_path / "pack"
    transition_dir = pack_dir / "src/example/transitions"
    transition_dir.mkdir(parents=True)
    (pack_dir / "evidence").mkdir()
    (pack_dir / "pyproject.toml").write_text(
        "[project]\nname = 'bad-pack'\nversion = '0.1.0'\n",
        encoding="utf-8",
    )
    (pack_dir / "evidence/seed_claims.yml").write_text(
        "claims:\n  - id: known-claim\n",
        encoding="utf-8",
    )
    (transition_dir / "bad.py").write_text(
        "\n".join(
            [
                "DEPENDENCIES = ['x']",
                "FIELDS_WRITTEN = ['y']",
                "EVIDENCE_CLAIMS = []",
                "COMPOSITION_RULE = 'replace'",
            ]
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/lint/pack-lint.py"), str(pack_dir)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    assert "EVIDENCE_CLAIMS must not be empty" in result.stderr
