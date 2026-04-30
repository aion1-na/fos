from __future__ import annotations

import sys
from pathlib import Path

import pytest

from fos_adapters import (
    AdapterCapability,
    AdapterRegistration,
    AdapterRegistry,
    adapter_schema_map,
)

ROOT = Path(__file__).resolve().parents[1]


def test_default_registry_registers_supported_adapters_without_importing_them() -> None:
    registry = AdapterRegistry.default()
    registrations = {item.adapter_id: item for item in registry.list()}

    assert set(registrations) == {
        "concordia",
        "cosmos_gl",
        "sigma_cytoscape",
        "mirofish_reference",
    }
    assert registrations["concordia"].trust_policy == "research_only"
    assert registrations["cosmos_gl"].capabilities == ("graph_layout", "graph_render")
    assert registrations["sigma_cytoscape"].trust_policy == "allowed"
    assert registrations["mirofish_reference"].trust_policy == "quarantined"

    for module_name in ["concordia", "cosmos", "cosmos_gl", "sigma", "cytoscape"]:
        assert module_name not in sys.modules


def test_registry_rejects_causal_capability_for_quarantined_adapters() -> None:
    registry = AdapterRegistry()
    for policy in ["quarantined", "research_only", "blocked"]:
        with pytest.raises(ValueError, match="non-allowed adapters"):
            registry.register(
                AdapterRegistration(
                    adapter_id=f"unsafe_tool_{policy}",
                    display_name="Unsafe tool",
                    version="not-installed",
                    trust_policy=policy,
                    capabilities=("causal_estimation",),
                )
            )


def test_blocked_adapter_execution_is_rejected() -> None:
    from fos_adapters import ToolArtifactReference, ToolExecutionManifest
    from fw_contracts import DatasetReference

    reference = DatasetReference(
        canonical_dataset_name="features.community_context",
        version="fixture-0.1",
        content_hash="a" * 64,
    )
    artifact = ToolArtifactReference(
        artifact_id="blocked-1",
        adapter_id="blocked_tool",
        artifact_type="tool",
        uri="artifact://blocked-1",
        content_hash="b" * 64,
        dataset_references=(reference,),
    )
    with pytest.raises(ValueError, match="blocked adapters"):
        ToolExecutionManifest(
            run_id="run-1",
            adapter_id="blocked_tool",
            adapter_version="not-installed",
            trust_policy="blocked",
            capabilities=("graph_render",),
            input_dataset_references=(reference,),
            artifacts=(artifact,),
        )


def test_adapter_capability_type_is_exhaustive_for_registry_contract() -> None:
    capability: AdapterCapability = "graph_render"
    assert capability == "graph_render"


def test_adapter_schemas_are_exported() -> None:
    schema_names = set(adapter_schema_map())
    assert schema_names >= {
        "AdapterRegistry",
        "ToolTrustPolicy",
        "AdapterCapability",
        "ToolArtifactReference",
        "ToolExecutionManifest",
    }
    for name in schema_names:
        assert (
            ROOT / "packages" / "fos-adapters" / "schemas" / f"{name}.schema.json"
        ).exists()
