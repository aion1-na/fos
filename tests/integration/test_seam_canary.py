from __future__ import annotations

import ast
from pathlib import Path

import fos_sim_kernel

ROOT = Path(__file__).resolve().parents[2]
KERNEL_SRC = ROOT / "packages" / "sim-kernel" / "src"
FORBIDDEN_KERNEL_STRINGS = ("flourishing", "GFS")


def _string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def test_sim_kernel_imports() -> None:
    assert fos_sim_kernel.__version__ == "0.1.0"


def test_kernel_has_no_pack_specific_strings() -> None:
    violations: list[str] = []
    for path in KERNEL_SRC.rglob("*.py"):
        for value in _string_literals(path):
            for forbidden in FORBIDDEN_KERNEL_STRINGS:
                if forbidden in value:
                    rel = path.relative_to(ROOT)
                    violations.append(f"{rel}: {forbidden}")

    assert violations == []
