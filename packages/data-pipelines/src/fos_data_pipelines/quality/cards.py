from __future__ import annotations

from pathlib import Path

REQUIRED_CARD_FIELDS = (
    "License metadata:",
    "Codebook mapping:",
    "Quality profile:",
    "Provenance manifest:",
    "Access policy:",
)


def lint_dataset_card(card_path: Path) -> list[str]:
    content = card_path.read_text(encoding="utf-8")
    return [field for field in REQUIRED_CARD_FIELDS if field not in content]


def detect_fixture_only_production_artifacts(paths: list[Path]) -> list[str]:
    defects: list[str] = []
    for path in paths:
        content = path.read_text(encoding="utf-8").lower()
        if "fixture_only" in content and "production_ready" in content:
            defects.append(f"{path}: fixture_only artifact cannot be production_ready")
    return defects
