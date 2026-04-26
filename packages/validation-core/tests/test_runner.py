from __future__ import annotations

from fw_contracts import DomainPack, SimulationRun, ValidationSuite
from fos_validation_core import run_validation_suite


def test_validation_suite_persists_report_shape() -> None:
    pack = DomainPack(
        id="pack",
        name="Pack",
        version="0.1.0",
        state_schema={"type": "object"},
        validation_suites=[ValidationSuite(id="suite-v0", checks=["gate"])],
    )
    run = SimulationRun(
        id="run-1",
        scenario_id="scenario-1",
        population_id="population-1",
        status="succeeded",
    )

    report = run_validation_suite(pack, run)

    assert report.id == "validation:run-1"
    assert report.suite_id == "suite-v0"
    assert report.status == "passed"
    assert report.metrics["headline_claims"][0]["e_value"] == 1.82
