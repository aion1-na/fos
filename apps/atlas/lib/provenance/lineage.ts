export interface DatasetReference {
  canonical_dataset_name: string;
  version: string;
  content_hash: string;
}

export interface ProvenanceNode {
  id: string;
  label: string;
  kind: "dataset" | "source" | "simulation_run";
}

export interface ProvenanceEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export const selectedDatasetReference: DatasetReference = {
  canonical_dataset_name: "features.community_context",
  version: "fixture-0.1",
  content_hash: "a".repeat(64),
};

export const provenanceNodes: ProvenanceNode[] = [
  {
    id: "source-community-fixture",
    label: "community_pathways_fixture.csv",
    kind: "source",
  },
  {
    id: "dataset-community-context",
    label: "features.community_context fixture-0.1",
    kind: "dataset",
  },
  {
    id: "run-fdw-smoke",
    label: "simulation-run-fdw-smoke",
    kind: "simulation_run",
  },
];

export const provenanceEdges: ProvenanceEdge[] = [
  {
    id: "fixture-feeds-dataset",
    source: "source-community-fixture",
    target: "dataset-community-context",
    label: "fed this dataset",
  },
  {
    id: "dataset-consumed-by-run",
    source: "dataset-community-context",
    target: "run-fdw-smoke",
    label: "consumed by simulation run",
  },
];
