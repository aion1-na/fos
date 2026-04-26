from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "apps" / "studio"
STAGE_ROUTES = [
    STUDIO / "app" / "studio" / "[stage]" / "page.tsx",
    STUDIO / "app" / "studio" / "population" / "page.tsx",
    STUDIO / "app" / "studio" / "configure" / "page.tsx",
    STUDIO / "app" / "studio" / "execute" / "page.tsx",
    STUDIO / "app" / "studio" / "validate" / "page.tsx",
    STUDIO / "app" / "studio" / "explore" / "page.tsx",
    STUDIO / "app" / "studio" / "brief" / "page.tsx",
]


def _contrast(hex_left: str, hex_right: str) -> float:
    def luminance(value: str) -> float:
        rgb = [int(value[index : index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4 for channel in rgb]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    left = luminance(hex_left)
    right = luminance(hex_right)
    lighter, darker = max(left, right), min(left, right)
    return (lighter + 0.05) / (darker + 0.05)


def test_stage_rail_has_keyboard_and_screen_reader_structure() -> None:
    rail = (STUDIO / "components" / "StageRail.tsx").read_text(encoding="utf-8")
    stages = (STUDIO / "lib" / "stages.ts").read_text(encoding="utf-8")
    assert 'aria-label="Studio stages"' in rail
    assert "aria-current" in rail
    assert "useStageStatus" in rail
    assert "STAGES.map" in rail
    assert stages.index('"frame"') < stages.index('"brief"')


def test_all_stage_pages_have_main_landmark_and_skip_target() -> None:
    layout = (STUDIO / "app" / "studio" / "layout.tsx").read_text(encoding="utf-8")
    assert 'href="#studio-main"' in layout
    assert 'aria-label="Stage context"' in layout
    for route in STAGE_ROUTES:
        source = route.read_text(encoding="utf-8")
        assert "<main" in source, route
        assert 'id="studio-main"' in source, route
        if "<h1" not in source:
            assert "PopulationInspector" in source, route
            inspector = (
                STUDIO / "components" / "population" / "PopulationInspector.tsx"
            ).read_text(encoding="utf-8")
            assert "<h1" in inspector


def test_contrast_tokens_meet_wcag_aa_for_normal_text() -> None:
    css = (STUDIO / "app" / "globals.css").read_text(encoding="utf-8")
    tokens = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6});", css))
    assert _contrast(tokens["ink"], tokens["bg"]) >= 4.5
    assert _contrast(tokens["muted"], tokens["panel"]) >= 4.5
    assert _contrast(tokens["accent"], tokens["panel"]) >= 4.5
    assert ".rail-link:focus-visible" in css
    assert ".skip-link:focus" in css


def test_cypress_axe_smoke_exists_for_every_stage() -> None:
    spec = (STUDIO / "cypress" / "e2e" / "accessibility.cy.ts").read_text(encoding="utf-8")
    support = (STUDIO / "cypress" / "support" / "axe.ts").read_text(encoding="utf-8")
    for stage in [
        "frame",
        "compose",
        "evidence",
        "population",
        "configure",
        "execute",
        "validate",
        "explore",
        "brief",
    ]:
        assert f"/studio/{stage}" in spec
    assert "checkA11y" in spec
    assert 'from "axe-core"' in support
