from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic import model_validator

CONTRACTS_VERSION = "0.1.0"

StageName = Literal[
    "frame",
    "compose",
    "evidence",
    "population",
    "configure",
    "execute",
    "validate",
    "explore",
    "brief",
]
StageStatusValue = Literal["empty", "pending", "ready", "running", "complete", "error"]
JsonObject = dict[str, Any]
T = TypeVar("T", bound=BaseModel)


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class OntologyRef(ContractModel):
    id: str
    version: str | None = None
    uri: str | None = None


class TransitionModel(ContractModel):
    id: str
    version: str
    entrypoint: str
    parameters_schema: JsonObject = Field(default_factory=dict)


class Intervention(ContractModel):
    id: str
    label: str
    parameters: JsonObject = Field(default_factory=dict)
    starts_at_step: int | None = Field(default=None, ge=0)
    ends_at_step: int | None = Field(default=None, ge=0)


class ValidationSuite(ContractModel):
    id: str
    checks: list[str] = Field(default_factory=list)
    parameters: JsonObject = Field(default_factory=dict)


class RenderHints(ContractModel):
    preferred_views: list[str] = Field(default_factory=list)
    encodings: JsonObject = Field(default_factory=dict)


class BranchSpec(ContractModel):
    id: str
    label: str
    parent_id: str | None = None
    parameters: JsonObject = Field(default_factory=dict)


class ShockSpec(ContractModel):
    id: str
    label: str
    at_step: int = Field(ge=0)
    parameters: JsonObject = Field(default_factory=dict)


class FidelityReport(ContractModel):
    level: Literal["low", "medium", "high"]
    notes: list[str] = Field(default_factory=list)
    metrics: JsonObject = Field(default_factory=dict)


class DatasetReference(ContractModel):
    canonical_dataset_name: str = Field(min_length=1, pattern=r"^[a-z0-9_][a-z0-9_.-]*$")
    version: str = Field(min_length=1)
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")

    def as_tuple(self) -> tuple[str, str, str]:
        return (self.canonical_dataset_name, self.version, self.content_hash)


class ToolArtifactReference(ContractModel):
    artifact_id: str
    adapter_id: str
    artifact_type: Literal["tool", "graph", "qualitative"]
    uri: str
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    dataset_references: list[DatasetReference] = Field(min_length=1)
    validated_for_causal_effects: bool = False
    notes: str = ""

    @model_validator(mode="after")
    def visual_and_qualitative_artifacts_are_not_effect_sizes(self) -> "ToolArtifactReference":
        if self.validated_for_causal_effects and self.artifact_type in {"graph", "qualitative"}:
            raise ValueError("graph and qualitative tool artifacts cannot create causal effect sizes")
        return self


class RunDataManifest(ContractModel):
    run_id: str
    scenario_id: str
    population_id: str
    dataset_references: list[DatasetReference] = Field(default_factory=list)
    touched_components: list[
        Literal[
            "population_synthesis",
            "transition_models",
            "validation",
            "adapter_artifacts",
        ]
    ] = Field(default_factory=list)
    tool_artifacts: list[ToolArtifactReference] = Field(default_factory=list)
    graph_artifacts: list[ToolArtifactReference] = Field(default_factory=list)
    qualitative_artifacts: list[ToolArtifactReference] = Field(default_factory=list)
    adapter_versions: dict[str, str] = Field(default_factory=dict)
    branch_id: str | None = None
    parent_branch_id: str | None = None
    manifest_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")

    def reference_tuples(self) -> tuple[tuple[str, str, str], ...]:
        return tuple(reference.as_tuple() for reference in self.dataset_references)


class DomainPack(ContractModel):
    id: str
    name: str
    version: str
    contracts_version: Literal["0.1.0"] = CONTRACTS_VERSION
    state_schema: JsonObject
    ontology: list[OntologyRef] = Field(default_factory=list)
    transition_models: list[TransitionModel] = Field(default_factory=list)
    validation_suites: list[ValidationSuite] = Field(default_factory=list)
    render_hints: RenderHints = Field(default_factory=RenderHints)


class Scenario(ContractModel):
    id: str
    domain_pack_id: str
    name: str
    stage_status: dict[StageName, StageStatusValue] = Field(default_factory=dict)
    ontology: list[OntologyRef] = Field(default_factory=list)
    interventions: list[Intervention] = Field(default_factory=list)
    branches: list[BranchSpec] = Field(default_factory=list)
    shocks: list[ShockSpec] = Field(default_factory=list)
    parameters: JsonObject = Field(default_factory=dict)


class AgentState(ContractModel, Generic[T]):
    agent_id: str
    step: int = Field(ge=0)
    state: T
    metadata: JsonObject = Field(default_factory=dict)


class Population(ContractModel):
    id: str
    scenario_id: str
    size: int = Field(ge=0)
    agent_ids: list[str] = Field(default_factory=list)
    metadata: JsonObject = Field(default_factory=dict)


class PopulationSnapshot(ContractModel, Generic[T]):
    id: str
    population_id: str
    step: int = Field(ge=0)
    agents: list[AgentState[T]] = Field(default_factory=list)
    created_at: datetime | None = None


class SpawnSpec(ContractModel):
    population_id: str
    count: int = Field(ge=0)
    state_seed: JsonObject = Field(default_factory=dict)
    metadata: JsonObject = Field(default_factory=dict)


class SimulationRun(ContractModel):
    id: str
    scenario_id: str
    population_id: str
    status: Literal["queued", "running", "succeeded", "failed", "cancelled"]
    started_at: datetime | None = None
    completed_at: datetime | None = None
    fidelity: FidelityReport | None = None
    outputs: JsonObject = Field(default_factory=dict)


class EvidenceClaim(ContractModel):
    id: str
    scenario_id: str
    transition_model_id: str
    statement: str
    source_id: str
    source_uri: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    target_population: str
    treatment: str
    comparator: str
    outcome_domain: str
    effect_size: float
    uncertainty: float = Field(ge=0.0)
    risk_of_bias: Literal["low", "medium", "high"]
    transportability: Literal["low", "medium", "high"]
    review_status: Literal["draft", "advisor_reviewed", "rejected", "superseded"]
    citation: str
    dataset_reference: DatasetReference
    metadata: JsonObject = Field(default_factory=dict)


class ValidationReport(ContractModel):
    id: str
    simulation_run_id: str
    suite_id: str
    status: Literal["passed", "failed", "warning"]
    claims: list[EvidenceClaim] = Field(default_factory=list)
    metrics: JsonObject = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


def assert_contracts_version(value: str) -> None:
    if value != CONTRACTS_VERSION:
        raise ValueError(
            f"Unsupported contracts version {value!r}; expected {CONTRACTS_VERSION!r}"
        )
