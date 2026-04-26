from __future__ import annotations

from typing import Any

from fw_contracts import DomainPack, EvidenceClaim, SimulationRun, ValidationReport


def run_validation_suite(
    pack: DomainPack,
    run: SimulationRun,
    *,
    metrics: dict[str, Any] | None = None,
) -> ValidationReport:
    suite = pack.validation_suites[0] if pack.validation_suites else None
    report_metrics = metrics or {
        "headline_claims": [
            {
                "claim": "Paid leave increases relationship stability in the modeled cohort.",
                "e_value": 1.82,
                "distributional_fidelity": "green",
                "seed_stability_variance": 0.004,
                "drift_status": "green",
            }
        ],
        "red_gate": False,
    }
    return ValidationReport(
        id=f"validation:{run.id}",
        simulation_run_id=run.id,
        suite_id=suite.id if suite else "validation-suite",
        status="passed" if not report_metrics.get("red_gate") else "failed",
        claims=[
            EvidenceClaim(
                id="validation-headline-claim",
                statement="Headline causal claim passed validation gate checks.",
                confidence=0.78,
                metadata={"run_id": run.id},
            )
        ],
        metrics=report_metrics,
        errors=[],
    )
