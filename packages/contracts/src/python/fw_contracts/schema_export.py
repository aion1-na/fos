from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from fw_contracts.models import (
    AgentState,
    BranchSpec,
    DomainPack,
    EvidenceClaim,
    FidelityReport,
    Intervention,
    OntologyRef,
    Population,
    PopulationSnapshot,
    RenderHints,
    Scenario,
    ShockSpec,
    SimulationRun,
    SpawnSpec,
    TransitionModel,
    ValidationReport,
    ValidationSuite,
)

SCHEMA_VERSION = "v0.1"

EXPORTED_MODELS: dict[str, type[BaseModel]] = {
    "DomainPack": DomainPack,
    "Scenario": Scenario,
    "AgentState": AgentState[BaseModel],
    "Population": Population,
    "PopulationSnapshot": PopulationSnapshot[BaseModel],
    "SpawnSpec": SpawnSpec,
    "SimulationRun": SimulationRun,
    "EvidenceClaim": EvidenceClaim,
    "ValidationReport": ValidationReport,
    "OntologyRef": OntologyRef,
    "TransitionModel": TransitionModel,
    "Intervention": Intervention,
    "ValidationSuite": ValidationSuite,
    "RenderHints": RenderHints,
    "BranchSpec": BranchSpec,
    "ShockSpec": ShockSpec,
    "FidelityReport": FidelityReport,
}


def schema_for(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema()


def write_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, model in EXPORTED_MODELS.items():
        path = output_dir / f"{name}.schema.json"
        path.write_text(
            json.dumps(schema_for(model), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    write_schemas(repo_root / "packages" / "contracts" / "schemas" / SCHEMA_VERSION)


if __name__ == "__main__":
    main()
