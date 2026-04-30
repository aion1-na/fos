import assert from "node:assert/strict";
import test from "node:test";

import {
  CONTRACTS_VERSION,
  parseDatasetReference,
  parseRunDataManifest,
  parseScenario,
} from "../../dist/ts/index.js";

test("exports contracts version", () => {
  assert.equal(CONTRACTS_VERSION, "0.1.0");
});

test("parses scenario-shaped data", () => {
  const scenario = parseScenario({
    id: "scenario-1",
    domain_pack_id: "pack-1",
    name: "Scenario",
    stage_status: { frame: "ready" },
  });

  assert.equal(scenario.id, "scenario-1");
  assert.equal(scenario.stage_status.frame, "ready");
});

test("parses dataset reference-shaped data", () => {
  const reference = parseDatasetReference({
    canonical_dataset_name: "features.community_context",
    version: "fixture-0.1",
    content_hash: "a".repeat(64),
  });

  assert.equal(reference.canonical_dataset_name, "features.community_context");
});

test("parses run data manifest-shaped data", () => {
  const manifest = parseRunDataManifest({
    run_id: "run-1",
    scenario_id: "scenario-1",
    population_id: "population-1",
    dataset_references: [
      {
        canonical_dataset_name: "features.community_context",
        version: "fixture-0.1",
        content_hash: "a".repeat(64),
      },
    ],
    touched_components: ["population_synthesis", "transition_models"],
  });

  assert.equal(manifest.dataset_references[0].version, "fixture-0.1");
});
