#!/usr/bin/env python3
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KERNEL_PATHS = [
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
    scan_paths = (
        [ROOT / arg for arg in sys.argv[1:]]
        if len(sys.argv) > 1
        else DEFAULT_KERNEL_PATHS
    )
    for package_path in scan_paths:
        if not package_path.exists():
            print(f"import-lint: path does not exist: {package_path}", file=sys.stderr)
            return 2

        paths = [package_path] if package_path.is_file() else package_path.rglob("*")
        for path in paths:
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
