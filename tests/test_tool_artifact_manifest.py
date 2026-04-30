from __future__ import annotations

import pytest
from pydantic import ValidationError

from fos_adapters import ToolArtifactReference, ToolExecutionManifest
from fw_contracts import DatasetReference, RunDataManifest


def _reference() -> DatasetReference:
    return DatasetReference(
        canonical_dataset_name="features.community_context",
        version="fixture-0.1",
        content_hash="a" * 64,
    )


def test_run_data_manifest_records_tool_artifacts_without_changing_dataset_contract() -> None:
    reference = _reference()
    graph_artifact = ToolArtifactReference(
        artifact_id="graph-layout-1",
        adapter_id="cosmos_gl",
        artifact_type="graph",
        uri="artifact://graph-layout-1",
        content_hash="b" * 64,
        dataset_references=(reference,),
        notes="visual artifact only",
    )

    manifest = RunDataManifest(
        run_id="run-1",
        scenario_id="scenario-1",
        population_id="population-1",
        dataset_references=[reference],
        touched_components=["population_synthesis", "transition_models", "validation"],
        graph_artifacts=[graph_artifact.model_dump(mode="json")],
        adapter_versions={"cosmos_gl": "not-installed"},
    )

    assert manifest.reference_tuples() == (reference.as_tuple(),)
    assert manifest.graph_artifacts[0].dataset_references[0].as_tuple() == reference.as_tuple()
    assert manifest.adapter_versions == {"cosmos_gl": "not-installed"}


def test_tool_execution_manifest_enforces_qualitative_causal_boundary() -> None:
    artifact = ToolArtifactReference(
        artifact_id="conversation-1",
        adapter_id="concordia",
        artifact_type="qualitative",
        uri="artifact://conversation-1",
        content_hash="c" * 64,
        dataset_references=(_reference(),),
        validated_for_causal_effects=True,
    )
    with pytest.raises(ValueError, match="qualitative adapters"):
        ToolExecutionManifest(
            run_id="run-1",
            adapter_id="concordia",
            adapter_version="not-installed",
            trust_policy="research_only",
            capabilities=("qualitative_interaction",),
            input_dataset_references=(_reference(),),
            artifacts=(artifact,),
            qualitative_only=True,
        )


def test_tool_artifacts_require_dataset_references() -> None:
    with pytest.raises(ValidationError):
        ToolArtifactReference(
            artifact_id="graph-layout-1",
            adapter_id="cosmos_gl",
            artifact_type="graph",
            uri="artifact://graph-layout-1",
            content_hash="d" * 64,
            dataset_references=(),
        )


def test_tool_artifacts_must_use_declared_input_references() -> None:
    input_reference = _reference()
    undeclared_reference = DatasetReference(
        canonical_dataset_name="features.other_context",
        version="fixture-0.1",
        content_hash="e" * 64,
    )
    artifact = ToolArtifactReference(
        artifact_id="graph-layout-1",
        adapter_id="cosmos_gl",
        artifact_type="graph",
        uri="artifact://graph-layout-1",
        content_hash="f" * 64,
        dataset_references=(undeclared_reference,),
    )

    with pytest.raises(ValueError, match="declared dataset_reference inputs"):
        ToolExecutionManifest(
            run_id="run-1",
            adapter_id="cosmos_gl",
            adapter_version="not-installed",
            trust_policy="allowed",
            capabilities=("graph_render",),
            input_dataset_references=(input_reference,),
            artifacts=(artifact,),
        )


def test_run_manifest_rejects_causal_qualitative_artifacts() -> None:
    with pytest.raises(ValidationError):
        RunDataManifest(
            run_id="run-1",
            scenario_id="scenario-1",
            population_id="population-1",
            qualitative_artifacts=[
                {
                    "artifact_id": "conversation-1",
                    "adapter_id": "concordia",
                    "artifact_type": "qualitative",
                    "uri": "artifact://conversation-1",
                    "content_hash": "1" * 64,
                    "dataset_references": [_reference().model_dump(mode="json")],
                    "validated_for_causal_effects": True,
                }
            ],
        )
