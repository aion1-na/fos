from __future__ import annotations

import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_contracts_and_packs_are_versioned_for_v0_1_0() -> None:
    package_paths = [
        ROOT / "packages" / "contracts" / "package.json",
        ROOT / "packs" / "toy-sir" / "package.json",
        ROOT / "packs" / "flourishing" / "package.json",
    ]
    pyproject_paths = [
        ROOT / "packages" / "contracts" / "pyproject.toml",
        ROOT / "packs" / "toy-sir" / "pyproject.toml",
        ROOT / "packs" / "flourishing" / "pyproject.toml",
    ]
    for path in package_paths:
        assert json.loads(path.read_text(encoding="utf-8"))["version"] == "0.1.0"
    for path in pyproject_paths:
        assert tomllib.loads(path.read_text(encoding="utf-8"))["project"]["version"] == "0.1.0"


def test_release_docs_are_present() -> None:
    required = [
        "docs/dev/monorepo.md",
        "docs/dev/contracts.md",
        "docs/dev/kernel.md",
        "docs/dev/pack-authoring.md",
        "docs/dev/studio.md",
        "docs/dev/deployment.md",
        "docs/research/scenarios.md",
        "docs/research/evidence-claims.md",
        "docs/research/validation-rubric.md",
        "docs/research/brief-reading.md",
        "docs/papers/ya-pilot-draft.md",
        "docs/risks/register.md",
        "CHANGELOG.md",
    ]
    for relative in required:
        path = ROOT / relative
        assert path.exists(), relative
        assert path.read_text(encoding="utf-8").strip(), relative
