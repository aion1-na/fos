from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CORE_PATHS = [
    ROOT / "apps",
    ROOT / "packages" / "contracts",
    ROOT / "packages" / "data-service",
    ROOT / "packages" / "sim-kernel",
    ROOT / "packs",
]


def _text_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and ".next" not in path.parts
        and "node_modules" not in path.parts
        and path.suffix
        in {
            ".json",
            ".md",
            ".mjs",
            ".py",
            ".schema",
            ".toml",
            ".ts",
            ".tsx",
            ".yaml",
            ".yml",
        }
    ]


def test_core_surfaces_use_fos_name() -> None:
    expected = [
        ROOT / "apps" / "api" / "src" / "fos_api" / "main.py",
        ROOT / "apps" / "atlas" / "app" / "layout.tsx",
        ROOT / "apps" / "studio" / "app" / "layout.tsx",
        ROOT / "packs" / "flourishing" / "render" / "brief_template.html",
    ]

    for path in expected:
        assert "FOS" in path.read_text(encoding="utf-8")


def test_user_facing_package_and_doc_labels_use_fos_name() -> None:
    scanned = [
        ROOT / "package.json",
        ROOT / "apps" / "studio" / "package.json",
        ROOT / "apps" / "studio" / "README.md",
        ROOT / "packages" / "contracts" / "package.json",
        ROOT / "packages" / "contracts" / "README.md",
        ROOT / "docs" / "contracts" / "v0.1.md",
        ROOT / "docs" / "dev" / "contracts.md",
        ROOT / "docs" / "dev" / "studio.md",
    ]
    for path in scanned:
        text = path.read_text(encoding="utf-8")
        assert "@fw/" not in text
        assert "fw-contracts" not in text
        assert "FDW" not in text


def test_core_has_no_mirofish_coupling() -> None:
    offenders: list[Path] = []
    for root in CORE_PATHS:
        for path in _text_files(root):
            if "fos-adapters" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            if "MiroFish" in text or "mirofish" in text:
                offenders.append(path.relative_to(ROOT))

    assert offenders == []
