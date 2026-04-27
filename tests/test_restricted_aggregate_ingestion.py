from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from fos_data_service.app import rdc_project_tracker, restricted_aggregate_ingest
from fos_data_service.catalog import AccessDeniedError, Catalog
from fos_data_service.secure_analysis import (
    AggregateResultSubmission,
    DisclosureReview,
    SecureAnalysisManifest,
    ingest_restricted_aggregate,
)

ROOT = Path(__file__).resolve().parents[1]


def _manifest() -> SecureAnalysisManifest:
    return SecureAnalysisManifest(
        project_id="census-rdc-lehd-displacement-calibration",
        environment="census_rdc",
        restricted_dataset_name="lehd",
        access_status="request_status_stub",
        raw_restricted_data_in_fdw_allowed=False,
        code_ref="git:analysis-pack@abc123",
        code_hash="a" * 64,
        environment_ref="container:sha256-bbb",
        environment_hash="b" * 64,
        intended_outputs=("lehd_displacement_event_rates_by_industry_region",),
        owner="Secure data lead",
        timeline="2026 Q3 proposal, 2026 Q4 disclosure-reviewed aggregates if approved",
    )


def _review(status: str = "approved") -> DisclosureReview:
    return DisclosureReview(
        status=status,
        reviewed_by="Disclosure reviewer",
        reviewed_on="2026-07-01",
        cell_suppression_checked=True,
        reidentification_risk_checked=True,
        publication_allowed=True,
        notes="Contract-test aggregate metadata only.",
    )


def _submission() -> AggregateResultSubmission:
    return AggregateResultSubmission(
        manifest=_manifest(),
        output_name="lehd_displacement_event_rates_by_industry_region",
        output_level="aggregate",
        aggregate_payload={
            "artifact_kind": "contract_test_aggregate",
            "rows": [],
            "note": "No restricted data or fabricated measurements.",
        },
        disclosure_review=_review(),
        canonical_dataset_name="features.lehd_displacement_aggregates",
        version="request-status-v0.1",
    )


def test_secure_manifest_rejects_raw_restricted_data_uri_without_terms() -> None:
    with pytest.raises(ValidationError, match="Tier 3 raw restricted data cannot be stored"):
        _manifest().model_copy(
            update={"raw_restricted_data_uri": "s3://fdw/restricted/lehd/raw.parquet"}
        ).model_validate(
            {
                **_manifest().model_dump(),
                "raw_restricted_data_uri": "s3://fdw/restricted/lehd/raw.parquet",
            }
        )


def test_disclosure_review_required_before_aggregate_ingestion() -> None:
    with pytest.raises(ValidationError, match="approved disclosure review"):
        AggregateResultSubmission(
            **{
                **_submission().model_dump(),
                "disclosure_review": _review(status="pending").model_dump(),
            }
        )


def test_restricted_aggregate_ingestion_creates_pinned_dataset_reference() -> None:
    first = ingest_restricted_aggregate(_submission())
    second = ingest_restricted_aggregate(_submission())

    assert first.dataset_reference == second.dataset_reference
    assert first.dataset_reference.canonical_dataset_name == "features.lehd_displacement_aggregates"
    assert first.dataset_reference.version == "request-status-v0.1"
    assert len(first.dataset_reference.content_hash) == 64
    assert first.stored_raw_restricted_data is False
    assert first.disclosure_review.approved_for_fdw is True


def test_catalog_rejects_restricted_aggregate_without_approved_disclosure() -> None:
    catalog = Catalog()
    record = ingest_restricted_aggregate(_submission())
    bad_record = record.model_copy(
        update={"disclosure_review": _review(status="pending")}
    )

    with pytest.raises(AccessDeniedError, match="approved disclosure review"):
        catalog.register_restricted_aggregate(bad_record)


def test_data_service_ingests_only_disclosure_approved_aggregates() -> None:
    payload = restricted_aggregate_ingest(_submission())

    assert payload["dataset_reference"]["canonical_dataset_name"] == (
        "features.lehd_displacement_aggregates"
    )
    assert payload["stored_raw_restricted_data"] is False
    assert payload["disclosure_review"]["status"] == "approved"
    assert payload["manifest_hash"]


def test_rdc_timeline_and_owners_are_visible_to_leadership() -> None:
    projects = rdc_project_tracker()["projects"]

    assert projects[0]["project_id"] == "census-rdc-lehd-displacement-calibration"
    assert projects[0]["owner"] == "Secure data lead"
    assert projects[0]["leadership_visible"] is True
    assert "timeline" in projects[0]


def test_tier3_docs_and_dataset_card_encode_required_boundaries() -> None:
    tracker = (ROOT / "docs/data/tier3/rdc-project-tracker.md").read_text(encoding="utf-8")
    template = (ROOT / "docs/data/tier3/analysis-pack-template.md").read_text(encoding="utf-8")
    checklist = (ROOT / "docs/data/tier3/disclosure-review-checklist.md").read_text(
        encoding="utf-8"
    )
    plan = (ROOT / "docs/data/tier3/lehd-displacement-analysis-plan.md").read_text(
        encoding="utf-8"
    )
    card = (ROOT / "docs/data/datasets/lehd-displacement-aggregates.md").read_text(
        encoding="utf-8"
    )

    assert "Tier 3 raw restricted data is never stored in FDW" in tracker
    assert "code_hash" in template
    assert "environment_hash" in template
    assert "intended_outputs" in template
    assert "Only aggregate outputs with approved disclosure-review metadata" in checklist
    assert "Raw LEHD restricted data must not enter FDW" in plan
    for required in [
        "License metadata:",
        "Codebook mapping:",
        "Quality profile:",
        "Provenance manifest:",
        "Access policy:",
    ]:
        assert required in card
