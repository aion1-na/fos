from __future__ import annotations

from pathlib import Path

from fos_data_pipelines.crosswalks.occupations import load_crosswalk

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "ai_exposure"


def test_soc_onet_census_crosswalk_is_versioned_and_preserves_source_codes() -> None:
    crosswalk = load_crosswalk(FIXTURES / "soc_onet_census_crosswalk_v0.1.csv", version="0.1")

    assert crosswalk.version == "0.1"
    assert crosswalk.soc_to_onet("15-1252") == "15-1252.00"
    assert crosswalk.onet_to_soc("15-1252.00") == "15-1252"
    assert crosswalk.census_to_canonical("1020") == "15-1252"
    assert {
        (row["soc_code"], row["onet_soc_code"], row["census_occ_code"], row["source_label"])
        for row in crosswalk.source_codes()
    } >= {("15-1252", "15-1252.00", "1020", "software developers")}
