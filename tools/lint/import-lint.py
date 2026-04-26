#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KERNEL_PATHS = [
    ROOT / "packages" / "sim-kernel",
    ROOT / "packages" / "population-synth",
    ROOT / "packages" / "validation-core",
    ROOT / "packages" / "render-core",
]
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
TEXT_IMPORT_RE = re.compile(
    r"""(?:import|export)\s+(?:[^'"]+\s+from\s+)?['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\)"""
)


def is_forbidden_specifier(specifier: str) -> bool:
    normalized = specifier.replace("\\", "/")
    return (
        normalized == "packs"
        or normalized.startswith("packs/")
        or "/packs/" in normalized
        or normalized.startswith("@fos/pack-")
        or normalized.startswith("fos_pack_")
    )


def python_imports(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [(exc.lineno or 1, f"<syntax-error: {exc.msg}>")]

    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.lineno, node.module))
    return imports


def text_imports(path: Path) -> list[tuple[int, str]]:
    imports: list[tuple[int, str]] = []
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        for match in TEXT_IMPORT_RE.finditer(line):
            imports.append((lineno, next(group for group in match.groups() if group)))
    return imports


def imports_for(path: Path) -> list[tuple[int, str]]:
    if path.suffix == ".py":
        return python_imports(path)
    return text_imports(path)


def main() -> int:
    violations: list[str] = []
    for package_path in KERNEL_PATHS:
        if not package_path.exists():
            continue
        for path in package_path.rglob("*"):
            if path.is_file() and path.suffix in SOURCE_SUFFIXES:
                for lineno, specifier in imports_for(path):
                    if is_forbidden_specifier(specifier):
                        rel = path.relative_to(ROOT)
                        violations.append(
                            f"{rel}:{lineno}: forbidden pack import: {specifier}"
                        )

    if violations:
        print("Kernel packages must not import from packs/:", file=sys.stderr)
        print("\n".join(violations), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
