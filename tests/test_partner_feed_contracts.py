from __future__ import annotations

import re
from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.partner_feeds import (
    build_real_time_labor_signals,
    load_partner_feed_contracts,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "partner_feeds"


def test_partner_feed_contracts_are_compartmentalized_and_secret_free() -> None:
    contracts = load_partner_feed_contracts(FIXTURES / "feed_contracts.json")
    assert {contract.canonical_dataset_name for contract in contracts} == {
        "lightcast_job_postings",
        "linkedin_hiring_signals",
        "indeed_job_postings",
    }
    for contract in contracts:
        assert contract.license_compartment.startswith("commercial/")
        assert contract.access_status == "request_status_stub"
        assert contract.license_status == "not_approved"
        assert contract.rows == []
        assert contract.ingest_allowed is False
        assert not re.search(r"token|secret|password|api[_-]?key", contract.model_dump_json(), re.I)


def test_real_time_labor_signal_snapshots_are_content_addressed(tmp_path: Path) -> None:
    output_path, reference = build_real_time_labor_signals(
        FIXTURES / "feed_contracts.json",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    assert reference.canonical_dataset_name == "features.real_time_labor_signals"
    assert len(rows) == 3
    for row in rows:
        assert row["feature_table"] == "features.real_time_labor_signals"
        assert row["content_hash"] == reference.content_hash
        assert row["dataset_reference"] == (
            f"(features.real_time_labor_signals, {reference.version}, {reference.content_hash})"
        )
        assert row["pinnable_by_run_manifest"] is True
        assert row["secret_free_contract_test"] is True
        assert row["partition_grain"] in {"daily", "hourly"}


def test_run_submission_snapshot_policy_requires_pinned_references() -> None:
    policy = (
        ROOT / "docs" / "data" / "partner-feeds" / "run-submission-snapshot-policy.md"
    ).read_text(encoding="utf-8")
    assert "Never read \"latest\" during a run" in policy
    assert "dataset_reference = (canonical_dataset_name, version, content_hash)" in policy
    assert "content-addressed" in policy


def test_commercial_data_cards_and_checklist_disclose_license_constraints() -> None:
    checklist = (
        ROOT
        / "docs"
        / "data"
        / "partner-feeds"
        / "commercial-data-evaluation-checklist.md"
    ).read_text(encoding="utf-8")
    assert "vendor-specific compartments" in checklist
    for slug in [
        "lightcast-job-postings",
        "linkedin-hiring-signals",
        "indeed-job-postings",
    ]:
        card = (ROOT / "docs" / "data" / "datasets" / f"{slug}.md").read_text(
            encoding="utf-8"
        )
        for required in [
            "License metadata:",
            "Codebook mapping:",
            "Quality profile:",
            "Provenance manifest:",
            "Access policy:",
        ]:
            assert required in card
        assert "no" in card.lower() and "committed" in card.lower()


def test_atlas_distinguishes_deployment_signals_from_predicted_exposure() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "labor-signals" / "page.tsx").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "apps" / "atlas" / "lib" / "labor" / "real-time.ts").read_text(
        encoding="utf-8"
    )
    assert "Real-time labor signals" in page
    assert "predicted exposure" in page
    assert "deployment signal" in source
