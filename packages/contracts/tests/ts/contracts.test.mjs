import assert from "node:assert/strict";
import test from "node:test";

import {
  CONTRACTS_VERSION,
  parseDatasetReference,
  parseRunDataManifest,
  parseScenario,
  parseToolArtifactReference,
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
    graph_artifacts: [
      {
        artifact_id: "graph-1",
        adapter_id: "cosmos_gl",
        artifact_type: "graph",
        uri: "artifact://graph-1",
        content_hash: "b".repeat(64),
        dataset_references: [
          {
            canonical_dataset_name: "features.community_context",
            version: "fixture-0.1",
            content_hash: "a".repeat(64),
          },
        ],
      },
    ],
    adapter_versions: { cosmos_gl: "not-installed" },
  });

  assert.equal(manifest.dataset_references[0].version, "fixture-0.1");
  assert.equal(manifest.graph_artifacts[0].adapter_id, "cosmos_gl");
});

test("rejects tool artifacts without dataset references", () => {
  assert.throws(
    () =>
      parseToolArtifactReference({
        artifact_id: "graph-1",
        adapter_id: "cosmos_gl",
        artifact_type: "graph",
        uri: "artifact://graph-1",
        content_hash: "b".repeat(64),
        dataset_references: [],
      }),
    /dataset_references must be nonempty/,
  );
});

test("rejects invalid nested dataset references in run manifests", () => {
  assert.throws(
    () =>
      parseRunDataManifest({
        run_id: "run-1",
        scenario_id: "scenario-1",
        population_id: "population-1",
        graph_artifacts: [
          {
            artifact_id: "graph-1",
            adapter_id: "cosmos_gl",
            artifact_type: "graph",
            uri: "artifact://graph-1",
            content_hash: "b".repeat(64),
            dataset_references: [
              {
                canonical_dataset_name: "features.community_context",
                version: "fixture-0.1",
                content_hash: "not-a-hash",
              },
            ],
          },
        ],
      }),
    /content_hash is invalid/,
  );
});
