from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIGURE_DIR = ROOT / "apps/studio/app/studio/configure"
EXECUTE_DIR = ROOT / "apps/studio/app/studio/execute"


def _source_files(path: Path) -> list[Path]:
    return sorted(file for file in path.rglob("*") if file.suffix in {".ts", ".tsx"})


def test_configure_and_execute_routes_do_not_import_each_other() -> None:
    violations: list[str] = []
    for file in _source_files(CONFIGURE_DIR):
        text = file.read_text(encoding="utf-8")
        if "app/studio/execute" in text or "../execute" in text:
            violations.append(str(file.relative_to(ROOT)))
    for file in _source_files(EXECUTE_DIR):
        text = file.read_text(encoding="utf-8")
        if "app/studio/configure" in text or "../configure" in text:
            violations.append(str(file.relative_to(ROOT)))

    assert violations == []


def test_configure_stage_has_save_run_spec_and_no_execute_button() -> None:
    text = (CONFIGURE_DIR / "page.tsx").read_text(encoding="utf-8")

    assert "Save run spec" in text
    assert ">Execute<" not in text
    assert '"Execute"' not in text


def test_execute_stage_keeps_run_parameters_read_only() -> None:
    text = (EXECUTE_DIR / "page.tsx").read_text(encoding="utf-8")

    assert "ReadOnlyRunSpec" in text
    assert "RuntimeTierPicker" not in text
    assert "SeedEnsembleSlider" not in text
