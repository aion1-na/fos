from __future__ import annotations

import json
from pathlib import Path

from fos_data_pipelines.us_panels import US_PANEL_CONSTRUCTS, load_panel_codebook, load_registration_stub

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "packages" / "data-pipelines" / "fixtures" / "us_panels"
PANELS = ["hrs", "midus", "nlsy79", "nlsy97", "psid"]


def test_registration_gated_connectors_are_request_status_stubs() -> None:
    for panel in PANELS:
        stub = load_registration_stub(FIXTURES / f"{panel}_registration_stub.json")
        assert stub["canonical_dataset_name"] == panel
        assert stub["access_status"] == "request_status_stub"
        assert stub["license_status"] == "not_approved"
        assert stub["registration_required"] is True
        assert stub["rows"] == []


def test_each_panel_has_source_specific_and_canonical_mappings() -> None:
    codebook = load_panel_codebook(FIXTURES / "harmonized_codebook.json")
    assert set(codebook["panels"]) == set(PANELS)
    for panel, mapping in codebook["panels"].items():
        assert set(mapping) == set(US_PANEL_CONSTRUCTS), panel
        for construct, source_variables in mapping.items():
            assert source_variables, (panel, construct)
            assert all(isinstance(variable, str) for variable in source_variables)


def test_wave_and_quality_metadata_cover_all_panels() -> None:
    wave_metadata = json.loads((FIXTURES / "wave_metadata.json").read_text(encoding="utf-8"))
    quality_profiles = json.loads((FIXTURES / "quality_profiles.json").read_text(encoding="utf-8"))
    assert set(wave_metadata) == set(PANELS)
    assert set(quality_profiles) == set(PANELS)
    for panel in PANELS:
        assert wave_metadata[panel]["country"] == "USA"
        assert quality_profiles[panel]["attrition_profile"] == "pending_access"
        assert quality_profiles[panel]["missingness_profile"] == "pending_access"
        assert quality_profiles[panel]["sampling_weight_profile"] == "pending_access"


def test_panel_dataset_cards_have_required_metadata() -> None:
    for panel in ["midus", "nlsy79", "nlsy97", "psid"]:
        card = (ROOT / "docs" / "data" / "datasets" / f"{panel}.md").read_text(
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
