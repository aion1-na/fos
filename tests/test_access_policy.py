from __future__ import annotations

from pathlib import Path

from fos_data_service.app import private_atlas_inventory, public_atlas_subset
from fos_data_service.catalog import AtlasAccessPolicy, Catalog

ROOT = Path(__file__).resolve().parents[1]


def test_public_atlas_subset_excludes_gated_restricted_and_license_constrained() -> None:
    public = public_atlas_subset()["datasets"]
    names = {dataset["canonical_dataset_name"] for dataset in public}
    assert "community-pathways" in names
    assert "hrs" not in names
    assert "commercial-labor-data" not in names
    assert all(dataset["scope"] == "public" for dataset in public)
    assert all(dataset["gated_reason"] is None for dataset in public)


def test_private_inventory_retains_gated_status_for_auditability() -> None:
    private = private_atlas_inventory()["datasets"]
    by_name = {dataset["canonical_dataset_name"]: dataset for dataset in private}
    assert by_name["hrs"]["gated_reason"] == "restricted_data_access"
    assert by_name["commercial-labor-data"]["gated_reason"] == "license_constrained"


def test_catalog_public_policy_fails_closed_when_gated() -> None:
    catalog = Catalog()
    catalog.register_atlas_access_policy(
        AtlasAccessPolicy(
            canonical_dataset_name="restricted-source",
            scope="public",
            tier="Tier 1",
            status="request_status_stub",
            limitations="Restricted source.",
            provenance_link="docs/data/datasets/restricted-source.md",
            gated_reason="restricted_data_access",
        )
    )
    assert catalog.public_atlas_policies() == []


def test_public_atlas_page_displays_tier_limitations_and_provenance() -> None:
    page = (ROOT / "apps" / "atlas" / "app" / "public" / "page.tsx").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "apps" / "atlas" / "lib" / "access" / "public.ts").read_text(
        encoding="utf-8"
    )
    assert "Tier" in page
    assert "Limitations" in page
    assert "Provenance" in page
    assert "publicAtlasDatasets" in source
    assert "license_constrained" in source


def test_search_and_citation_generation_covers_cards_codebooks_and_claims() -> None:
    source = (ROOT / "apps" / "atlas" / "lib" / "search" / "citations.ts").read_text(
        encoding="utf-8"
    )
    page = (ROOT / "apps" / "atlas" / "app" / "search" / "page.tsx").read_text(
        encoding="utf-8"
    )
    for kind in ["dataset_card", "codebook", "evidence_claim"]:
        assert kind in source
    assert "searchCitations" in source
    assert "Sign-off" in page
    assert "Provenance" in page


def test_preregistration_packet_has_required_policy_sections() -> None:
    packet = (
        ROOT / "docs" / "data" / "governance" / "osf-preregistration-draft.md"
    ).read_text(encoding="utf-8")
    for required in [
        "Scenario Definition",
        "Validation Gates",
        "Seed Policy",
        "Dataset Version Policy",
    ]:
        assert required in packet


def test_signoff_status_visible_per_construct_codebook_and_claim() -> None:
    signoff = (ROOT / "docs" / "data" / "governance" / "signoff-log.json").read_text(
        encoding="utf-8"
    )
    assert "constructs" in signoff
    assert "codebooks" in signoff
    assert "evidence_claims" in signoff
    assert "pending_advisor_review" in signoff
    assert "claim_mentoring_meaning_v0" in signoff
