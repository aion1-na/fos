from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq
import yaml

from fos_data_pipelines.codebooks import load_codebook
from fos_data_pipelines.connectors.acs_ipums import parse_acs_fixture
from fos_data_pipelines.connectors.bls_oews import parse_bls_oews_fixture
from fos_data_pipelines.connectors.onet import parse_onet_fixture
from fos_data_pipelines.dataset_cards import render_dataset_card

ROOT = Path(__file__).resolve().parents[1]
CODEBOOKS = ROOT / "codebooks"
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures"


def test_construct_dictionary_has_scientific_review_queue() -> None:
    constructs = yaml.safe_load((CODEBOOKS / "constructs.yaml").read_text(encoding="utf-8"))

    assert constructs["version"] == "0.1"
    assert constructs["scientific_review_queue"] == "docs/data/review/construct-change-queue.md"
    assert {item["canonical_name"] for item in constructs["constructs"]} >= {
        "age",
        "occupation_code",
        "hourly_wage",
    }


def test_codebook_mappings_preserve_original_labels_and_canonical_names() -> None:
    acs = load_codebook(CODEBOOKS / "acs_person.yaml")
    onet = load_codebook(CODEBOOKS / "onet.yaml")
    bls = load_codebook(CODEBOOKS / "bls_oews.yaml")

    assert acs.source_to_canonical["AGE"] == "age"
    assert acs.original_labels["age"] == "Age"
    assert onet.source_to_canonical["onetsoc_code"] == "occupation_code"
    assert onet.original_labels["occupation_code"] == "O*NET-SOC Code"
    assert bls.source_to_canonical["h_mean"] == "hourly_wage"
    assert bls.original_labels["hourly_wage"] == "Mean hourly wage"


def test_acs_onet_and_bls_fixtures_parse_to_staged_parquet(tmp_path: Path) -> None:
    acs = parse_acs_fixture(
        FIXTURES / "acs" / "person_fixture.csv",
        CODEBOOKS / "acs_person.yaml",
        tmp_path / "acs",
    )
    onet = parse_onet_fixture(
        FIXTURES / "onet" / "occupation_fixture.json",
        CODEBOOKS / "onet.yaml",
        tmp_path / "onet",
    )
    bls = parse_bls_oews_fixture(
        FIXTURES / "bls" / "oews_fixture.json",
        CODEBOOKS / "bls_oews.yaml",
        tmp_path / "bls",
    )

    for artifact in (acs, onet, bls):
        path = Path(artifact.stage_uri.removeprefix("file://"))
        table = pq.read_table(path)
        assert path.suffix == ".parquet"
        assert artifact.row_count == 2
        assert table.num_rows == 2

    assert "age" in pq.read_table(Path(acs.stage_uri.removeprefix("file://"))).column_names
    assert "skill_name" in pq.read_table(Path(onet.stage_uri.removeprefix("file://"))).column_names
    assert "hourly_wage" in pq.read_table(Path(bls.stage_uri.removeprefix("file://"))).column_names


def test_dataset_card_template_renderer_includes_metadata() -> None:
    rendered = render_dataset_card(
        ROOT / "docs" / "data" / "dataset-card-template.md",
        {
            "canonical_dataset_name": "acs_ipums",
            "version": "fixture-0.1",
            "license": "request-status stub",
            "content_hash": "a" * 64,
            "fetch_timestamp": "fixture-only",
            "codebook_ref": "codebooks/acs_person.yaml",
            "quality_profile_ref": "fixture quality profile",
            "provenance_manifest_ref": "fixture provenance manifest",
            "access_policy_ref": "fixture access policy",
            "notes": "No production access approved.",
        },
    )

    assert "Dataset Card: acs_ipums" in rendered
    assert "`fixture-0.1`" in rendered
    assert "request-status stub" in rendered
    assert "a" * 64 in rendered
