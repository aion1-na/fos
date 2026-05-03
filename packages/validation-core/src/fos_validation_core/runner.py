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
                scenario_id=run.scenario_id,
                transition_model_id="validation_summary",
                statement="Headline causal claim passed validation gate checks.",
                source_id="validation_fixture_only",
                confidence=0.78,
                target_population="fixture validation cohort",
                treatment="validation gate pass",
                comparator="validation gate fail",
                outcome_domain="validation_status",
                effect_size=0.0,
                uncertainty=0.0,
                risk_of_bias="high",
                transportability="low",
                review_status="draft",
                citation="FOS validation-core fixture_only runner.",
                dataset_reference={
                    "canonical_dataset_name": "validation_core.fixture_only",
                    "version": "fixture-0.1",
                    "content_hash": "0" * 64,
                },
                metadata={"run_id": run.id},
            )
        ],
        metrics=report_metrics,
        errors=[],
    )
