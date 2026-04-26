export const packageName = "@fos/render-core";

export type AgentInstance = {
  id: string;
  x: number;
  y: number;
  color: string;
  size: number;
  institutionId?: string;
};

export type InstitutionBuilding = {
  id: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
};

export type InstancedWorld = {
  agents: AgentInstance[];
  institutions: InstitutionBuilding[];
  budgetMsPerFrame: number;
};

export type RenderFieldHint = {
  key: string;
  label: string;
  kind: "continuous" | "categorical";
  tab: "composition" | "networks" | "institutions" | "fidelity" | "provenance";
  domain?: [number, number];
};

export type PopulationRenderHints = {
  fields: RenderFieldHint[];
  colorBy: string;
  institutionField: string;
};

function colorForIndex(index: number): string {
  const palette = ["#27715f", "#5b7fbd", "#b45f3a", "#7b6db5", "#c08b2c", "#3b8f8c"];
  return palette[index % palette.length];
}

export function buildInstancedWorld(
  agents: Array<{ id: string; institutionId?: string }>,
  institutions: Array<{ id: string; label: string }>,
): InstancedWorld {
  const columns = Math.ceil(Math.sqrt(agents.length));
  const institutionLookup = new Map(institutions.map((institution, index) => [institution.id, index]));
  return {
    budgetMsPerFrame: 16,
    agents: agents.map((agent, index) => {
      const institutionIndex = institutionLookup.get(agent.institutionId ?? "") ?? 0;
      return {
        id: agent.id,
        x: (index % columns) / columns,
        y: Math.floor(index / columns) / columns,
        color: colorForIndex(institutionIndex),
        size: 2,
        institutionId: agent.institutionId,
      };
    }),
    institutions: institutions.map((institution, index) => ({
      id: institution.id,
      label: institution.label,
      x: 0.04 + index * 0.15,
      y: 0.06,
      width: 0.10,
      height: 0.08,
      color: colorForIndex(index),
    })),
  };
}
