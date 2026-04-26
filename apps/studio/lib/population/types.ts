import type { PopulationRenderHints } from "@fos/render-core";

export type FidelityStatus = "green" | "amber" | "red";

export type AttributeDistribution = {
  key: string;
  label: string;
  kind: "continuous" | "categorical";
  tab: "composition" | "networks" | "institutions" | "fidelity" | "provenance";
  bins: Array<{ label: string; value: number }>;
  ks: number;
  status: FidelityStatus;
};

export type AgentRecord = {
  id: string;
  institutionId: string;
  fields: Record<string, string | number | boolean>;
};

export type InstitutionRecord = {
  id: string;
  label: string;
  members: number;
};

export type PopulationInspectorData = {
  id: string;
  name: string;
  packId: string;
  count: number;
  createdAt: string;
  renderHints: PopulationRenderHints;
  distributions: AttributeDistribution[];
  networks: Array<{ id: string; label: string; density: number; meanDegree: number; status: FidelityStatus }>;
  institutions: InstitutionRecord[];
  provenance: Array<{ label: string; value: string }>;
  agents: AgentRecord[];
};

export type CohortFilter = {
  populationId: string;
  field: string;
  operator: ">=" | "<=" | "=";
  value: string | number | boolean;
};

export type CohortArtifact = {
  id: string;
  target_population: string;
  filters: CohortFilter[];
  agent_ids: string[];
};
