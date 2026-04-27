from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTNER_DATASETS = [
    "hrs",
    "soep",
    "understanding-society",
    "gfs",
    "anthropic-economic-index",
    "census-rdc",
    "commercial-labor-data",
]
DATASETS = [
    *PARTNER_DATASETS,
    "acs-ipums",
    "onet",
    "bls-oews",
]
WORKSTREAM_READMES = [
    "packages/data-pipelines/README.md",
    "packages/data-service/README.md",
    "packages/contracts/README.md",
    "apps/atlas/README.md",
    "infra/README.md",
]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_codex_data_instructions_set_safe_defaults() -> None:
    instructions = _read(".codex/instructions.md")
    for phrase in [
        "Do not fabricate data",
        "Do not perform unversioned reads",
        "Do not make undocumented transformations",
        "Do not introduce silent schema changes",
        "Do not commit real credentials",
        "dataset_reference = (canonical_dataset_name, version, content_hash)",
    ]:
        assert phrase in instructions


def test_partnership_trackers_and_dataset_cards_exist_as_request_status_stubs() -> None:
    for slug in PARTNER_DATASETS:
        tracker = _read(f"docs/data/partnerships/{slug}.md")
        dataset_card = _read(f"docs/data/datasets/{slug}.md")
        assert "Access status: request-status stub" in tracker
        assert "DUA status: not approved" in tracker
        assert "Access status: request-status stub" in dataset_card
    for slug in DATASETS:
        dataset_card = _read(f"docs/data/datasets/{slug}.md")
        for required in [
            "License metadata:",
            "Codebook mapping:",
            "Quality profile:",
            "Provenance manifest:",
            "Access policy:",
        ]:
            assert required in dataset_card


def test_workstream_readmes_have_owner_test_command_and_definition_of_done() -> None:
    for relative in WORKSTREAM_READMES:
        content = _read(relative)
        assert "Owner:" in content, relative
        assert "Test command:" in content, relative
        assert "Definition of done:" in content, relative


def test_backlog_maps_each_drd_section_to_a_sprint() -> None:
    backlog = _read("docs/data/backlog.md")
    for index in range(1, 11):
        assert f"DRD-{index:02d}" in backlog
    assert "| DRD Section | Sprint | Outcome |" in backlog


def test_atlas_dataset_directory_lists_required_metadata() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "datasets" / "page.tsx").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "apps" / "atlas" / "lib" / "datasets.ts").read_text(encoding="utf-8")
    for field in ["version", "license", "contentHash", "fetchTimestamp", "cardLink"]:
        assert field in source
        assert field in page
    for dataset in ["acs_ipums", "onet", "bls_oews"]:
        assert dataset in source


def test_no_connector_or_dashboard_credentials_are_committed() -> None:
    scanned_roots = [
        ROOT / "apps" / "atlas",
        ROOT / "packages" / "data-service",
        ROOT / "packages" / "data-pipelines",
        ROOT / "infra",
    ]
    forbidden = re.compile(
        r"(aws_access_key_id|aws_secret_access_key|api[_-]?key\s*[:=]\s*['\"][^'\"]+|"
        r"password\s*[:=]\s*['\"][^'\"]+|token\s*[:=]\s*['\"][^'\"]+|"
        r"sk-[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]+)",
        re.IGNORECASE,
    )
    for root in scanned_roots:
        for path in root.rglob("*"):
            if path.is_dir() or path.suffix in {".pyc", ".gz"}:
                continue
            if any(part in {".next", "node_modules", "__pycache__"} for part in path.parts):
                continue
            content = path.read_text(encoding="utf-8")
            assert not forbidden.search(content), path


def test_platform_code_does_not_read_raw_files_directly() -> None:
    platform_roots = [
        ROOT / "apps" / "api",
        ROOT / "apps" / "studio",
        ROOT / "packages" / "sim-kernel",
        ROOT / "packages" / "population-synth",
        ROOT / "packages" / "validation-core",
        ROOT / "packages" / "render-core",
    ]
    forbidden = re.compile(r"(fos_data_pipelines\.raw_zone|RawZone|/raw/|s3://fos-raw)")
    for root in platform_roots:
        for path in root.rglob("*"):
            if path.is_dir() or path.suffix in {".pyc", ".gz", ".pack"}:
                continue
            if any(part in {".next", "node_modules", "__pycache__"} for part in path.parts):
                continue
            content = path.read_text(encoding="utf-8")
            assert not forbidden.search(content), path
