from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from hypothesis import given, settings, strategies as st
from pydantic import BaseModel

from fw_contracts import (
    CONTRACTS_VERSION,
    AgentState,
    DatasetReference,
    DomainPack,
    RunDataManifest,
    Scenario,
)
from fw_contracts.schema_export import EXPORTED_MODELS

ROOT = Path(__file__).resolve().parents[4]
CODEGEN_DONE = False


class ToyState(BaseModel):
    value: int
    label: str


def ts_roundtrip(model_name: str, payload: dict) -> dict:
    global CODEGEN_DONE
    if not CODEGEN_DONE:
        subprocess.run(
            [sys.executable, "tools/codegen/contracts_to_ts.py"],
            cwd=ROOT,
            check=True,
        )
        CODEGEN_DONE = True

    script = f"""
      import fs from "node:fs";
      import {{ parse{model_name} }} from "./packages/contracts/dist/ts/index.js";
      const input = JSON.parse(fs.readFileSync(0, "utf8"));
      const parsed = parse{model_name}(input);
      process.stdout.write(JSON.stringify(parsed));
    """
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        input=json.dumps(payload),
        text=True,
    )
    return json.loads(result.stdout)


def test_version_export() -> None:
    assert CONTRACTS_VERSION == "0.1.0"


def test_dataset_reference_is_content_addressed_tuple() -> None:
    reference = DatasetReference(
        canonical_dataset_name="features.community_context",
        version="fixture-0.1",
        content_hash="a" * 64,
    )

    assert reference.as_tuple() == ("features.community_context", "fixture-0.1", "a" * 64)


def test_dataset_reference_roundtrips_through_ts() -> None:
    reference = DatasetReference(
        canonical_dataset_name="features.community_context",
        version="fixture-0.1",
        content_hash="b" * 64,
    )
    returned = ts_roundtrip("DatasetReference", reference.model_dump(mode="json"))
    assert DatasetReference.model_validate(returned) == reference


def test_run_data_manifest_roundtrips_through_ts() -> None:
    manifest = RunDataManifest(
        run_id="run-1",
        scenario_id="scenario-1",
        population_id="population-1",
        dataset_references=[
            DatasetReference(
                canonical_dataset_name="features.community_context",
                version="fixture-0.1",
                content_hash="c" * 64,
            )
        ],
        touched_components=[
            "population_synthesis",
            "transition_models",
            "validation",
            "mirofish_adapter",
        ],
        branch_id="baseline",
        manifest_hash="d" * 64,
    )

    returned = ts_roundtrip("RunDataManifest", manifest.model_dump(mode="json"))
    assert RunDataManifest.model_validate(returned) == manifest


def test_schema_exports_exist() -> None:
    schema_dir = ROOT / "packages" / "contracts" / "schemas" / "v0.1"
    for model_name in EXPORTED_MODELS:
        assert (schema_dir / f"{model_name}.schema.json").exists()


def test_agent_state_is_generic_over_pack_state() -> None:
    state = AgentState[ToyState](
        agent_id="agent-1",
        step=3,
        state=ToyState(value=7, label="opaque"),
    )

    assert state.state.value == 7


def test_domain_pack_asserts_contract_version() -> None:
    pack = DomainPack(
        id="toy",
        name="Toy",
        version="0.1.0",
        contracts_version=CONTRACTS_VERSION,
        state_schema={"type": "object"},
    )

    assert pack.contracts_version == CONTRACTS_VERSION


def test_scenario_empty_stage_status_roundtrips_through_ts() -> None:
    scenario = Scenario(
        id="0",
        domain_pack_id="0",
        name="0",
        stage_status={"frame": "empty"},
    )

    returned = ts_roundtrip("Scenario", scenario.model_dump(mode="json"))
    assert Scenario.model_validate(returned) == scenario


@settings(max_examples=100, deadline=None)
@given(
    scenario_id=st.text(min_size=1, max_size=20),
    pack_id=st.text(min_size=1, max_size=20),
    name=st.text(min_size=1, max_size=30),
    frame_status=st.sampled_from(
        ["empty", "pending", "ready", "running", "complete", "error"]
    ),
)
def test_scenario_roundtrips_through_ts(
    scenario_id: str,
    pack_id: str,
    name: str,
    frame_status: str,
) -> None:
    scenario = Scenario(
        id=scenario_id,
        domain_pack_id=pack_id,
        name=name,
        stage_status={"frame": frame_status},
    )
    payload = scenario.model_dump(mode="json")
    returned = ts_roundtrip("Scenario", payload)
    assert Scenario.model_validate(returned) == scenario
