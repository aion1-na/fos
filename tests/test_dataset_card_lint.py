from __future__ import annotations

from pathlib import Path

from fos_data_pipelines.quality import lint_dataset_card, validate_tier1_release_candidate
from fos_data_pipelines.quality.cards import detect_fixture_only_production_artifacts

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "packages" / "data-pipelines" / "fixtures" / "tier1" / "tier1_manifest.json"
EXPECTATIONS = (
    ROOT / "packages" / "data-pipelines" / "fixtures" / "tier1" / "expectation_suites.json"
)


def test_tier1_dataset_cards_are_complete() -> None:
    defects = validate_tier1_release_candidate(MANIFEST, EXPECTATIONS, ROOT)
    assert defects == []


def test_dataset_card_linter_reports_missing_required_metadata(tmp_path: Path) -> None:
    incomplete = tmp_path / "incomplete.md"
    incomplete.write_text(
        "\n".join(
            [
                "# Incomplete",
                "License metadata: fixture",
                "Codebook mapping: fixture",
            ]
        ),
        encoding="utf-8",
    )
    missing = lint_dataset_card(incomplete)
    assert "Quality profile:" in missing
    assert "Provenance manifest:" in missing
    assert "Access policy:" in missing


def test_fixture_only_detector_blocks_production_markers(tmp_path: Path) -> None:
    card = tmp_path / "fixture.md"
    card.write_text(
        "canonical_dataset_name: fixture_only\nproduction_ready: true\n",
        encoding="utf-8",
    )

    defects = detect_fixture_only_production_artifacts([card])

    assert defects
    assert "fixture_only artifact cannot be production_ready" in defects[0]


def test_release_candidate_manifest_documents_tier1_scope() -> None:
    manifest = (ROOT / "docs" / "data" / "tier1-release-candidate.json").read_text(
        encoding="utf-8"
    )
    assert "tier1-rc0" in manifest
    assert "offline fixture and request-status validation only" in manifest
    assert "community-pathways" in manifest
