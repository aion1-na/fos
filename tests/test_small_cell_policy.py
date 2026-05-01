from __future__ import annotations

from pathlib import Path

import pyarrow.parquet as pq

from fos_data_pipelines.health_public.context import (
    CELL_SUPPRESSION_THRESHOLD,
    assert_public_health_policy_columns,
    build_health_validation_context,
    parse_public_health_stub,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "health_public"


def test_small_mortality_cells_are_suppressed(tmp_path: Path) -> None:
    output_path, _ = build_health_validation_context(
        FIXTURES / "cdc_mortality_fixture_only.csv",
        tmp_path,
    )
    rows = pq.read_table(output_path).to_pylist()
    suppressed = [row for row in rows if row["suppressed"]]

    assert CELL_SUPPRESSION_THRESHOLD == 10
    assert suppressed
    assert all(row["deaths"] is None for row in suppressed)
    assert all(row["mortality_rate"] is None for row in suppressed)


def test_sensitive_health_columns_are_rejected() -> None:
    try:
        assert_public_health_policy_columns({"country_code", "ssn"})
    except ValueError as error:
        assert "sensitive fields" in str(error)
    else:
        raise AssertionError("sensitive health field was allowed")


def test_public_health_request_status_rows_are_rejected(tmp_path: Path) -> None:
    stub = tmp_path / "bad_health_stub.json"
    stub.write_text(
        '{"access_status": "request_status_stub", "rows": [{"fake": true}]}',
        encoding="utf-8",
    )
    try:
        parse_public_health_stub(stub)
    except ValueError as error:
        assert "must not include table rows" in str(error)
    else:
        raise AssertionError("request-status health rows were accepted")
