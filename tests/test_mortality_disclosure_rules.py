from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from fos_data_service.app import (
    nchs_access_tracker,
    restricted_mortality_aggregate_ingest,
)
from fos_data_service.catalog import AccessDeniedError, Catalog
from fos_data_service.restricted_health import (
    MortalityAggregateRow,
    RestrictedMortalityAggregateRecord,
    RestrictedMortalityAggregateSubmission,
    SourceEnvironmentMetadata,
    ingest_restricted_mortality_aggregate,
)

ROOT = Path(__file__).resolve().parents[1]


def _environment(public_cdc_wonder_output: bool = False) -> SourceEnvironmentMetadata:
    return SourceEnvironmentMetadata(
        environment="nchs_rdc",
        steward="NCHS RDC",
        access_status="request_status_stub",
        disclosure_protocol="RDC disclosure review required before export",
        public_cdc_wonder_output=public_cdc_wonder_output,
    )


def _visible_row() -> MortalityAggregateRow:
    return MortalityAggregateRow(
        geography_level="state",
        geography_label="CO",
        demographic_fields=("age_band", "sex", "cause_group"),
        cause_group="deaths_of_despair",
        deaths=12,
        mortality_rate=14.2,
        suppressed=False,
        suppression_rule="deaths < 10 suppressed",
    )


def _submission() -> RestrictedMortalityAggregateSubmission:
    return RestrictedMortalityAggregateSubmission(
        source_environment=_environment(),
        approval_status="approved",
        review_id="nchs-review-001",
        canonical_dataset_name="features.restricted_mortality_aggregates",
        version="request-status-v0.1",
        rows=(_visible_row(),),
        intended_use="health-domain mortality calibration",
    )


def test_small_cell_suppression_is_codified() -> None:
    with pytest.raises(ValidationError, match="small-cell threshold"):
        MortalityAggregateRow(
            geography_level="state",
            geography_label="CO",
            demographic_fields=("age_band", "sex", "cause_group"),
            cause_group="deaths_of_despair",
            deaths=9,
            mortality_rate=10.1,
            suppressed=False,
            suppression_rule="deaths < 10 suppressed",
        )

    with pytest.raises(ValidationError, match="cannot expose deaths or rate"):
        MortalityAggregateRow(
            geography_level="state",
            geography_label="CO",
            demographic_fields=("age_band", "sex", "cause_group"),
            cause_group="deaths_of_despair",
            deaths=3,
            mortality_rate=2.1,
            suppressed=True,
            suppression_rule="deaths < 10 suppressed",
        )


def test_prohibited_geography_and_demographics_are_not_atlas_safe() -> None:
    with pytest.raises(ValidationError, match="county geography is prohibited"):
        _visible_row().model_copy(update={"geography_level": "county"}).model_validate(
            {**_visible_row().model_dump(), "geography_level": "county"}
        )

    with pytest.raises(ValidationError, match="prohibited demographic detail"):
        _visible_row().model_copy(
            update={"demographic_fields": ("age_band", "race_ethnicity_detail")}
        ).model_validate(
            {
                **_visible_row().model_dump(),
                "demographic_fields": ("age_band", "race_ethnicity_detail"),
            }
        )


def test_restricted_path_rejects_public_cdc_wonder_outputs() -> None:
    with pytest.raises(ValidationError, match="CDC WONDER"):
        RestrictedMortalityAggregateSubmission(
            **{
                **_submission().model_dump(),
                "source_environment": _environment(public_cdc_wonder_output=True).model_dump(),
            }
        )


def test_every_restricted_aggregate_has_approval_and_source_environment_metadata() -> None:
    record = ingest_restricted_mortality_aggregate(_submission())

    assert record.dataset_reference.canonical_dataset_name == (
        "features.restricted_mortality_aggregates"
    )
    assert record.dataset_reference.version == "request-status-v0.1"
    assert len(record.dataset_reference.content_hash) == 64
    assert record.approval_status == "approved"
    assert record.source_environment.environment == "nchs_rdc"
    assert record.stored_raw_restricted_data is False


def test_catalog_rejects_unapproved_restricted_health_output() -> None:
    catalog = Catalog()
    record = ingest_restricted_mortality_aggregate(_submission())
    bad_record = RestrictedMortalityAggregateRecord(
        **{**record.model_dump(), "approval_status": "pending_disclosure_review"}
    )

    with pytest.raises(AccessDeniedError, match="approved status"):
        catalog.register_restricted_mortality_aggregate(bad_record)


def test_data_service_restricted_mortality_ingest_returns_atlas_safe_rows() -> None:
    payload = restricted_mortality_aggregate_ingest(_submission())

    assert payload["dataset_reference"]["canonical_dataset_name"] == (
        "features.restricted_mortality_aggregates"
    )
    assert payload["approval_status"] == "approved"
    assert payload["source_environment"]["environment"] == "nchs_rdc"
    assert payload["source_environment"]["public_cdc_wonder_output"] is False
    assert payload["atlas_safe_rows"][0]["geography_level"] == "state"
    assert "county" not in str(payload["atlas_safe_rows"]).lower()


def test_nchs_access_tracker_is_request_status_only() -> None:
    projects = nchs_access_tracker()["projects"]

    assert projects[0]["project_id"] == "nchs-rdc-mortality-despair-validation"
    assert projects[0]["access_status"] == "request_status_stub"
    assert projects[0]["irb_dua_status"] == "not_submitted"


def test_restricted_health_docs_capture_disclosure_and_separation_rules() -> None:
    docs = [
        ROOT / "docs/data/restricted-health/nchs-access-tracker.md",
        ROOT / "docs/data/restricted-health/irb-dua-checklist.md",
        ROOT / "docs/data/restricted-health/state-vital-statistics-opportunity-map.md",
        ROOT / "docs/data/restricted-health/health-to-mortality-calibration-plan.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    card = (ROOT / "docs/data/datasets/restricted-mortality-aggregates.md").read_text(
        encoding="utf-8"
    )

    assert "Restricted mortality outputs are not CDC WONDER public table outputs" in combined
    assert "Minimum unsuppressed cell count: 10" in combined
    assert "Atlas-visible geography is limited to national, state, or region" in combined
    assert "No state vital statistics data is assumed available" in combined
    for required in [
        "License metadata:",
        "Codebook mapping:",
        "Quality profile:",
        "Provenance manifest:",
        "Access policy:",
    ]:
        assert required in card
