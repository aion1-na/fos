from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.connectors import (
    atus_public_time_use_connector_config,
    ess_connector_config,
    eurostat_connector_config,
    gss_connector_config,
    ilo_connector_config,
    oecd_connector_config,
    opportunity_atlas_connector_config,
    parse_public_context_stub,
    parse_request_status_stub,
    pew_religious_landscape_connector_config,
    social_capital_atlas_connector_config,
    volunteering_civic_life_connector_config,
    world_bank_connector_config,
    world_happiness_report_connector_config,
    wvs_connector_config,
)
from fos_data_pipelines.community import (
    build_community_context,
    build_social_capital_context,
    build_time_use_context,
    load_request_status_stub,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "community_context"


def test_community_features_join_only_to_valid_geographies(tmp_path: Path) -> None:
    output_path, reference = build_community_context(
        FIXTURES / "community_pathways_fixture.csv",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    assert reference.canonical_dataset_name == "features.community_context"
    assert reference.as_tuple()[0] == "features.community_context"
    assert {row["geography_level"] for row in rows} == {"county", "zip", "tract"}
    assert all(row["join_allowed"] for row in rows)
    assert "private_archive" not in {row["source_geography_id"] for row in rows}
    assert all("dataset_reference" in row for row in rows)
    assert all(len(row["content_hash"]) == 64 for row in rows)
    assert {row["codebook_version"] for row in rows} == {"0.1"}


def test_time_use_and_social_capital_context_outputs_are_referenced(tmp_path: Path) -> None:
    time_path, time_reference = build_time_use_context(
        FIXTURES / "time_use_fixture.csv",
        tmp_path,
    )
    social_path, social_reference = build_social_capital_context(
        FIXTURES / "community_pathways_fixture.csv",
        tmp_path,
    )
    time_rows = pq.read_table(time_path).to_pylist()
    social_rows = pq.read_table(social_path).to_pylist()
    assert time_reference.canonical_dataset_name == "features.time_use_context"
    assert social_reference.canonical_dataset_name == "features.social_capital_context"
    assert {row["measure"] for row in time_rows} == {"caregiving_hours", "social_hours"}
    assert "trust" in {row["construct"] for row in social_rows}
    assert "volunteering" in {row["construct"] for row in social_rows}


def test_archive_limited_sources_are_request_status_stubs() -> None:
    for name in [
        "religious_attendance_stub.json",
        "social_capital_archive_stub.json",
        "gss_public_context_stub.json",
        "pew_religious_landscape_stub.json",
        "volunteering_civic_life_stub.json",
        "social_capital_atlas_stub.json",
        "opportunity_atlas_stub.json",
    ]:
        stub = parse_request_status_stub(FIXTURES / name)
        assert stub["access_status"] == "request_status_stub"
        assert stub["rows"] == []
        assert "fake" not in str(stub).lower()

    assert load_request_status_stub(FIXTURES / "religious_attendance_stub.json")[
        "access_status"
    ] == "request_status_stub"


def test_dataset_cards_disclose_limitations_and_inappropriate_uses() -> None:
    for slug in [
        "community-pathways",
        "atus-public-time-use",
        "social-capital-context",
    ]:
        content = (ROOT / "docs" / "data" / "datasets" / f"{slug}.md").read_text(
            encoding="utf-8"
        )
        assert "License metadata:" in content
        assert "Codebook mapping:" in content
        assert "Quality profile:" in content
        assert "Provenance manifest:" in content
        assert "Access policy:" in content
        assert "Inappropriate uses:" in content
        assert "limitations" in content.lower()


def test_rs05_connector_configs_have_metadata_refs() -> None:
    configs = [
        factory("https://example.org/public-metadata")
        for factory in [
            gss_connector_config,
            atus_public_time_use_connector_config,
            pew_religious_landscape_connector_config,
            volunteering_civic_life_connector_config,
            social_capital_atlas_connector_config,
            opportunity_atlas_connector_config,
            world_happiness_report_connector_config,
            ess_connector_config,
            wvs_connector_config,
            oecd_connector_config,
            world_bank_connector_config,
            eurostat_connector_config,
            ilo_connector_config,
        ]
    ]

    assert {config.dataset_version for config in configs} == {"request-status-v0.1"}
    for config in configs:
        assert (ROOT / config.codebook_ref).exists()
        assert (ROOT / config.license_ref.split("#", 1)[0]).exists()
        assert config.quality_profile_ref.endswith("#quality-profile")
        assert config.provenance_manifest_ref.endswith("#provenance-manifest")
        assert config.access_policy_ref.endswith("#access-policy")


def test_public_context_stubs_do_not_contain_rows() -> None:
    fixture_dir = ROOT / "packages" / "data-pipelines" / "fixtures" / "cross_validation"
    for name in [
        "oecd_public_context_stub.json",
        "world_bank_public_context_stub.json",
        "eurostat_public_context_stub.json",
        "ilo_public_context_stub.json",
    ]:
        stub = parse_public_context_stub(fixture_dir / name)
        assert stub["access_status"] == "request_status_stub"
        assert stub["rows"] == []


def test_atlas_evidence_graph_can_traverse_to_dataset() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "evidence-graph" / "page.tsx").read_text(
        encoding="utf-8"
    )
    graph = (ROOT / "apps" / "atlas" / "lib" / "evidence" / "graph.ts").read_text(
        encoding="utf-8"
    )
    assert "React Flow" in page
    assert "construct -> evidence claim" in graph
    assert "evidence claim -> citation" in graph
    assert "citation -> dataset" in graph
    for field in ["construct", "claim", "source", "confidenceLabel"]:
        assert field in graph
