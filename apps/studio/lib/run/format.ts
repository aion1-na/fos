import type { RunSpec } from "@/lib/run/types";

export function formatRunSpecRows(spec: RunSpec): Array<{ label: string; value: string }> {
  return [
    { label: "Run spec", value: spec.id },
    { label: "Branch", value: spec.branch },
    { label: "Agents", value: spec.agentCount.toLocaleString() },
    { label: "Horizon", value: `${spec.horizonMonths} months` },
    { label: "Seeds", value: spec.seeds.toLocaleString() },
    { label: "Runtime tier", value: spec.runtimeTier },
    { label: "Evidence", value: spec.evidenceMode },
    { label: "Validation gates", value: spec.validationGates ? "enabled" : "disabled" },
    { label: "Draft", value: spec.draft ? "yes" : "no" },
  ];
}
