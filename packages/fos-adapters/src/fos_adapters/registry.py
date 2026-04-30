from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Literal

from fw_contracts import DatasetReference
from pydantic import BaseModel, ConfigDict, Field, model_validator

AdapterCapability = Literal[
    "qualitative_interaction",
    "cognition_trace",
    "graph_layout",
    "graph_render",
    "network_analysis",
    "causal_estimation",
]
ToolTrustPolicy = Literal["allowed", "quarantined", "blocked", "research_only"]


class AdapterRegistration(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    adapter_id: str = Field(min_length=1, pattern=r"^[a-z0-9_][a-z0-9_.-]*$")
    display_name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    trust_policy: ToolTrustPolicy
    capabilities: tuple[AdapterCapability, ...]
    import_path: str | None = None
    notes: str = Field(default="", max_length=2000)

    @property
    def can_create_causal_effect_sizes(self) -> bool:
        return "causal_estimation" in self.capabilities and self.trust_policy == "allowed"


class ToolArtifactReference(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_id: str = Field(min_length=1)
    adapter_id: str = Field(min_length=1)
    artifact_type: Literal["tool", "graph", "qualitative"]
    uri: str = Field(min_length=1)
    content_hash: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    dataset_references: tuple[DatasetReference, ...] = Field(min_length=1)
    validated_for_causal_effects: bool = False
    notes: str = ""


class ToolExecutionManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str = Field(min_length=1)
    adapter_id: str = Field(min_length=1)
    adapter_version: str = Field(min_length=1)
    trust_policy: ToolTrustPolicy
    capabilities: tuple[AdapterCapability, ...]
    input_dataset_references: tuple[DatasetReference, ...] = Field(min_length=1)
    artifacts: tuple[ToolArtifactReference, ...] = Field(min_length=1)
    executed_at: datetime | None = None
    qualitative_only: bool = True

    @model_validator(mode="after")
    def enforce_trust_boundaries(self) -> "ToolExecutionManifest":
        self.assert_dataset_contracts()
        if self.trust_policy == "blocked":
            raise ValueError("blocked adapters must not execute")
        if self.trust_policy != "allowed" and "causal_estimation" in self.capabilities:
            raise ValueError("non-allowed adapters cannot claim causal_estimation capability")
        return self

    def assert_dataset_contracts(self) -> None:
        if not self.input_dataset_references:
            raise ValueError("adapter execution requires dataset_reference inputs")
        input_tuples = {reference.as_tuple() for reference in self.input_dataset_references}
        for artifact in self.artifacts:
            if not artifact.dataset_references:
                raise ValueError("tool artifacts must retain dataset_reference inputs")
            if artifact.validated_for_causal_effects and self.qualitative_only:
                raise ValueError("qualitative adapters cannot emit causal effect sizes")
            for reference in artifact.dataset_references:
                DatasetReference.model_validate(reference)
                if reference.as_tuple() not in input_tuples:
                    raise ValueError("tool artifacts must use declared dataset_reference inputs")


class AdapterRegistry:
    def __init__(self) -> None:
        self._registrations: dict[str, AdapterRegistration] = {}

    def register(self, registration: AdapterRegistration) -> AdapterRegistration:
        if registration.adapter_id in self._registrations:
            raise ValueError(f"adapter {registration.adapter_id!r} is already registered")
        if (
            registration.trust_policy != "allowed"
            and "causal_estimation" in registration.capabilities
        ):
            raise ValueError("non-allowed adapters cannot claim causal_estimation capability")
        self._registrations[registration.adapter_id] = registration
        return registration

    def get(self, adapter_id: str) -> AdapterRegistration:
        return self._registrations[adapter_id]

    def list(self) -> tuple[AdapterRegistration, ...]:
        return tuple(self._registrations[key] for key in sorted(self._registrations))

    def by_policy(self, policy: ToolTrustPolicy) -> tuple[AdapterRegistration, ...]:
        return tuple(item for item in self.list() if item.trust_policy == policy)

    @classmethod
    def default(cls) -> AdapterRegistry:
        registry = cls()
        registry.register(
            AdapterRegistration(
                adapter_id="concordia",
                display_name="Concordia",
                version="not-installed",
                trust_policy="research_only",
                capabilities=("qualitative_interaction", "cognition_trace"),
                notes=(
                    "Registered as a qualitative interaction/cognition adapter; outputs "
                    "do not create causal effect sizes without separate validation."
                ),
            )
        )
        registry.register(
            AdapterRegistration(
                adapter_id="cosmos_gl",
                display_name="cosmos.gl renderer",
                version="not-installed",
                trust_policy="allowed",
                capabilities=("graph_layout", "graph_render"),
                notes="FOS Graph visual renderer; graph layout is not evidence.",
            )
        )
        registry.register(
            AdapterRegistration(
                adapter_id="sigma_cytoscape",
                display_name="Sigma/Cytoscape fallback",
                version="not-installed",
                trust_policy="allowed",
                capabilities=("graph_layout", "graph_render", "network_analysis"),
                notes="Fallback graph renderer and analytic helper; visual artifacts are not evidence.",
            )
        )
        registry.register(
            AdapterRegistration(
                adapter_id="mirofish_reference",
                display_name="MiroFish reference",
                version="not-installed",
                trust_policy="quarantined",
                capabilities=("qualitative_interaction",),
                notes="Quarantined legacy reference. It is not imported by FOS core.",
            )
        )
        return registry


class AdapterRegistrySchema(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    registrations: tuple[AdapterRegistration, ...]


def adapter_schema_map() -> dict[str, dict[str, object]]:
    return {
        "AdapterRegistry": AdapterRegistrySchema.model_json_schema(),
        "AdapterRegistration": AdapterRegistration.model_json_schema(),
        "ToolArtifactReference": ToolArtifactReference.model_json_schema(),
        "ToolExecutionManifest": ToolExecutionManifest.model_json_schema(),
        "ToolTrustPolicy": {
            "title": "ToolTrustPolicy",
            "type": "string",
            "enum": ["allowed", "quarantined", "blocked", "research_only"],
        },
        "AdapterCapability": {
            "title": "AdapterCapability",
            "type": "string",
            "enum": [
                "qualitative_interaction",
                "cognition_trace",
                "graph_layout",
                "graph_render",
                "network_analysis",
                "causal_estimation",
            ],
        },
    }


def write_adapter_schemas(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, schema in adapter_schema_map().items():
        (output_dir / f"{name}.schema.json").write_text(
            json.dumps(schema, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
