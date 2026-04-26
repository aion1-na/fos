#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _literal_list(module: ast.Module, name: str) -> list[str]:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                        raise ValueError(f"{name} must be a list[str]")
                    return value
    raise ValueError(f"missing {name}")


def _literal_str(module: ast.Module, name: str) -> str:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    if not isinstance(value, str):
                        raise ValueError(f"{name} must be a string")
                    return value
    raise ValueError(f"missing {name}")


def _claim_ids(evidence_path: Path) -> set[str]:
    ids: set[str] = set()
    for line in evidence_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- id:"):
            ids.add(stripped.split(":", 1)[1].strip().strip("'\""))
    return ids


def _project_version(pyproject_path: Path) -> str:
    in_project = False
    for line in pyproject_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project = False
        if in_project and stripped.startswith("version"):
            return stripped.split("=", 1)[1].strip().strip("'\"")
    return ""


def lint_pack(pack_dir: Path) -> list[str]:
    errors: list[str] = []
    pyproject_path = pack_dir / "pyproject.toml"
    if not pyproject_path.exists():
        return [f"{pack_dir}: missing pyproject.toml"]

    version = _project_version(pyproject_path)
    if not SEMVER.fullmatch(version):
        errors.append(f"{pack_dir}: project.version must be semver")

    evidence_ids = _claim_ids(pack_dir / "evidence" / "seed_claims.yml")
    transition_dir = next((pack_dir / "src").glob("*/transitions"))
    written_by: dict[str, str] = {}
    for path in sorted(transition_dir.glob("*.py")):
        if path.name in {"__init__.py", "common.py"}:
            continue
        module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        try:
            evidence_claims = _literal_list(module, "EVIDENCE_CLAIMS")
            fields_written = _literal_list(module, "FIELDS_WRITTEN")
            dependencies = _literal_list(module, "DEPENDENCIES")
            composition_rule = _literal_str(module, "COMPOSITION_RULE")
        except ValueError as exc:
            errors.append(f"{path}: {exc}")
            continue
        if not evidence_claims:
            errors.append(f"{path}: EVIDENCE_CLAIMS must not be empty")
        unknown = sorted(set(evidence_claims) - evidence_ids)
        if unknown:
            errors.append(f"{path}: unknown evidence claims {unknown}")
        if not dependencies:
            errors.append(f"{path}: DEPENDENCIES must not be empty")
        if not fields_written:
            errors.append(f"{path}: FIELDS_WRITTEN must not be empty")
        if composition_rule != "replace":
            errors.append(f"{path}: COMPOSITION_RULE must be 'replace'")
        for field in fields_written:
            previous = written_by.get(field)
            if previous is not None:
                errors.append(f"{path}: field {field!r} also written by {previous}")
            written_by[field] = path.name
    return errors


def main() -> int:
    roots = [Path(arg) for arg in sys.argv[1:]] or [Path("packs/flourishing")]
    errors: list[str] = []
    for root in roots:
        errors.extend(lint_pack(root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
