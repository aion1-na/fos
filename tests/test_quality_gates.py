from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa

from fos_data_pipelines.quality import (
    FEATURE_TABLE_SCHEMA,
    HARMONIZED_TABLE_SCHEMA,
    STAGED_TABLE_SCHEMA,
    load_expectation_suites,
    run_quality_gate,
)
from fos_data_service.catalog import Catalog

ROOT = Path(__file__).resolve().parents[1]
EXPECTATIONS = (
    ROOT / "packages" / "data-pipelines" / "fixtures" / "tier1" / "expectation_suites.json"
)


def test_quality_gate_reports_counts_missingness_distributions_pii_and_sampling() -> None:
    table = pa.table(
        {
            "age": [18, 19, None],
            "sex": ["F", "M", "F"],
            "occupation_code": ["15-0000", "43-0000", "43-0000"],
            "wage": [15.0, 22.0, None],
        }
    )
    suites = load_expectation_suites(EXPECTATIONS)
    report = run_quality_gate(
        "acs-ipums",
        table,
        suites["acs-ipums"],
        sampling_metadata={"fixture_source": "acs/person_fixture.csv", "survey_year": "2021"},
    )
    assert report.row_count == 3
    assert report.missingness["age"] == 1
    assert report.missingness["wage"] == 1
    assert report.distributions["occupation_code"]["43-0000"] == 2
    assert report.pii_candidates == []
    assert report.sampling_metadata["survey_year"] == "2021"
    assert report.required_columns_present is True


def test_quality_gate_detects_missing_required_columns() -> None:
    table = pa.table({"age": [18]})
    suites = load_expectation_suites(EXPECTATIONS)
    report = run_quality_gate("acs-ipums", table, suites["acs-ipums"])
    assert report.required_columns_present is False


def test_pandera_schema_specs_cover_staged_harmonized_and_feature_tables() -> None:
    assert STAGED_TABLE_SCHEMA.table_stage == "staged"
    assert HARMONIZED_TABLE_SCHEMA.table_stage == "harmonized"
    assert FEATURE_TABLE_SCHEMA.table_stage == "feature"
    assert "dataset_reference" in FEATURE_TABLE_SCHEMA.required_columns()


def test_catalog_policy_blocks_production_without_complete_metadata() -> None:
    catalog = Catalog()
    try:
        catalog.register_dataset_policy(
            "acs-ipums",
            tier="Tier 1",
            status="approved_production",
            production_ready=True,
            metadata_fields={"License metadata:", "Codebook mapping:"},
        )
    except ValueError as exc:
        assert "cannot be production-ready" in str(exc)
    else:
        raise AssertionError("production-ready dataset with missing metadata was accepted")


def test_expectation_suite_exists_for_every_tier1_manifest_dataset() -> None:
    manifest = json.loads(
        (
            ROOT
            / "packages"
            / "data-pipelines"
            / "fixtures"
            / "tier1"
            / "tier1_manifest.json"
        ).read_text(encoding="utf-8")
    )
    suites = load_expectation_suites(EXPECTATIONS)
    for dataset in manifest["datasets"]:
        assert dataset["canonical_dataset_name"] in suites
