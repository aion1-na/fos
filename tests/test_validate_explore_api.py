from __future__ import annotations

from fos_api.main import (
    FindingRequest,
    OverrideRequest,
    get_run_causal_trace,
    get_run_validation,
    list_run_findings,
    record_run_override,
    save_run_finding,
)


def test_validation_endpoint_exposes_trust_wedge_metrics() -> None:
    payload = get_run_validation("run-1")
    claims = payload["headline_claims"]

    assert payload["brief_export_blocked"] is True
    assert any(claim["gate"] == "red" for claim in claims)
    for claim in claims:
        assert "e_value" in claim
        assert "distributional_fidelity" in claim
        assert "seed_stability_variance" in claim
        assert "drift_status" in claim


def test_causal_trace_endpoint_labels_exploratory_pathways() -> None:
    payload = get_run_causal_trace("run-1")
    exploratory = [pathway for pathway in payload["pathways"] if not pathway["calibrated"]]

    assert exploratory
    assert all(pathway["evidence_claim_id"] is None for pathway in exploratory)
    assert all("confidence_interval" in pathway for pathway in payload["pathways"])
    assert all("shapley_value" in pathway for pathway in payload["pathways"])


def test_saved_findings_are_stable_artifacts() -> None:
    request = FindingRequest(
        title="Finding",
        claim="Claim",
        source="validate",
        artifact_refs=["validation:run-1"],
        assumptions=["Reviewed"],
    )

    first = save_run_finding("run-1", request)
    second = save_run_finding("run-1", request)
    findings = list_run_findings("run-1")["findings"]

    assert first["id"] == second["id"]
    assert first["id"] in {finding["id"] for finding in findings}


def test_override_entries_appear_in_validation_audit_log() -> None:
    justification = (
        "Amber gate is overridden for this internal review because the sensitivity "
        "analysis is documented and downstream brief assumptions will cite it."
    )

    override = record_run_override(
        "run-override",
        OverrideRequest(gate="amber", justification=justification),
    )
    validation = get_run_validation("run-override")

    assert override["event"] == "validation_gate_override_recorded"
    assert override in validation["audit_log"]
    assert override["assumptions"][0].endswith(justification)
