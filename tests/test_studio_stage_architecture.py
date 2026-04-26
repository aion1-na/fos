from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIGURE_DIR = ROOT / "apps/studio/app/studio/configure"
EXECUTE_DIR = ROOT / "apps/studio/app/studio/execute"
STATUS_MACHINE = ROOT / "apps/studio/lib/stageStatusMachine.ts"


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


def test_stage_status_machine_covers_every_scope_8_4_1_row() -> None:
    text = STATUS_MACHINE.read_text(encoding="utf-8")
    expected_rows = [
        "8.4.1-empty-edit",
        "8.4.1-pending-save",
        "8.4.1-ready-start",
        "8.4.1-running-complete",
        "8.4.1-running-fail",
        "8.4.1-error-retry",
        "8.4.1-complete-upstream",
        "8.4.1-ready-upstream",
    ]

    for row_id in expected_rows:
        assert row_id in text


def test_execute_stage_declares_stream_log_and_kpi_components() -> None:
    text = (EXECUTE_DIR / "page.tsx").read_text(encoding="utf-8")

    assert "RunConsoleStream" in text
    assert "EventLogTail" not in text
    assert "KpiTraceChart" not in text


def test_validate_and_explore_routes_include_required_surfaces() -> None:
    validate = (ROOT / "apps/studio/app/studio/validate/page.tsx").read_text(encoding="utf-8")
    explore = (ROOT / "apps/studio/app/studio/explore/page.tsx").read_text(encoding="utf-8")

    for token in [
        "ClaimGateTable",
        "BriefExportGate",
        "CausalTraceDecomposition",
        "FindingSaveButton",
        "runId={RUN_ID}",
    ]:
        assert token in validate
    for token in [
        "BranchViewer",
        "CausalTraceOverlay",
        "SixDomainRadar",
        "SubgroupBreakdownTable",
        "UnintendedConsequenceList",
        "RepresentativeAgentPanel",
        "FindingSaveButton",
    ]:
        assert token in explore


def test_override_dialog_requires_fifty_character_justification_and_brief_assumptions() -> None:
    override_dialog = (ROOT / "apps/studio/components/validation/OverrideDialog.tsx").read_text(encoding="utf-8")
    brief = (ROOT / "apps/studio/app/studio/brief/page.tsx").read_text(encoding="utf-8")
    trace = (ROOT / "apps/studio/components/validation/CausalTraceDecomposition.tsx").read_text(encoding="utf-8")

    assert "trimmed.length >= 50" in override_dialog
    assert "/overrides" in override_dialog
    assert "overridesForRun(RUN_ID)" in brief
    assert "Assumptions" in brief
    assert "Cited evidence claim id" in trace
