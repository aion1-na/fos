import type { AgentRecord, CohortArtifact, CohortFilter } from "@/lib/population/types";

function stableJson(value: unknown): string {
  if (Array.isArray(value)) {
    return `[${value.map(stableJson).join(",")}]`;
  }
  if (value && typeof value === "object") {
    return `{${Object.entries(value)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, entry]) => `${JSON.stringify(key)}:${stableJson(entry)}`)
      .join(",")}}`;
  }
  return JSON.stringify(value);
}

export async function contentAddress(value: unknown): Promise<string> {
  const encoded = new TextEncoder().encode(stableJson(value));
  const digest = await crypto.subtle.digest("SHA-256", encoded);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function matchesFilter(agent: AgentRecord, filter: CohortFilter): boolean {
  const value = agent.fields[filter.field];
  if (typeof value === "number" && typeof filter.value === "number") {
    if (filter.operator === ">=") {
      return value >= filter.value;
    }
    if (filter.operator === "<=") {
      return value <= filter.value;
    }
  }
  return value === filter.value;
}

export async function saveCohort(
  agents: AgentRecord[],
  filters: CohortFilter[],
): Promise<CohortArtifact> {
  const agentIds = agents
    .filter((agent) => filters.every((filter) => matchesFilter(agent, filter)))
    .map((agent) => agent.id)
    .sort();
  const targetPopulation = filters[0]?.populationId ?? "";
  const payload = {
    target_population: targetPopulation,
    filters,
    agent_ids: agentIds,
  };
  return {
    id: `cohort_${(await contentAddress(payload)).slice(0, 24)}`,
    target_population: targetPopulation,
    filters,
    agent_ids: agentIds,
  };
}
