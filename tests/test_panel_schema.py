from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines.panels import PANEL_REQUIRED_COLUMNS, PanelSchema, panel_query_keys

ROOT = Path(__file__).resolve().parents[1]


def test_panel_schema_declares_required_longitudinal_columns() -> None:
    schema = PanelSchema()
    assert schema.required_columns() == PANEL_REQUIRED_COLUMNS
    for column in [
        "person_id",
        "household_id",
        "wave",
        "country",
        "weights",
        "outcomes",
        "treatments",
        "attrition_metadata",
    ]:
        assert column in schema.required_columns()


def test_panel_schema_supports_wave_and_person_level_queries() -> None:
    keys = panel_query_keys()
    assert keys["person_level"] == ("person_id", "wave")
    assert keys["wave_level"] == ("country", "wave")
    assert keys["household_level"] == ("household_id", "wave")


def test_timescaledb_migration_declares_panel_views() -> None:
    migration = (
        ROOT / "packages" / "data-service" / "migrations" / "003_tier2_panels.sql"
    ).read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS timescaledb" in migration
    assert "CREATE TABLE IF NOT EXISTS tier2.longitudinal_panel" in migration
    assert "person_id TEXT NOT NULL" in migration
    assert "household_id TEXT NOT NULL" in migration
    assert "wave INTEGER NOT NULL" in migration
    assert "weights JSONB NOT NULL" in migration
    assert "attrition_metadata JSONB NOT NULL" in migration
    assert "CREATE MATERIALIZED VIEW IF NOT EXISTS tier2.panel_person_wave" in migration
    assert "CREATE MATERIALIZED VIEW IF NOT EXISTS tier2.panel_wave_summary" in migration


def test_pending_dua_connector_stubs_do_not_include_rows() -> None:
    fixture_dir = ROOT / "packages" / "data-pipelines" / "fixtures" / "tier2"
    expected = {
        "hrs_stub.json",
        "soep_stub.json",
        "understanding_society_stub.json",
        "census_rdc_stub.json",
        "commercial_labor_data_stub.json",
    }
    assert {path.name for path in fixture_dir.glob("*_stub.json")} == expected
    for path in fixture_dir.glob("*_stub.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["access_status"] == "request_status_stub"
        assert payload["license_status"] == "not_approved"
        assert payload["rows"] == []
