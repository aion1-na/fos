export type RuntimeTier = "draft" | "standard" | "audit";

export type RunSpec = {
  id: string;
  branch: string;
  seeds: number;
  horizonMonths: number;
  agentCount: number;
  runtimeTier: RuntimeTier;
  evidenceMode: "fixture-only" | "pack-default";
  validationGates: boolean;
  kpis: string[];
  shocks: string[];
  draft: boolean;
};

export type InvalidatedArtifact = {
  id: string;
  stage: string;
  reason: string;
  regenerationCost: string;
};

export const DRAFT_RUN_SPEC: RunSpec = {
  id: "run_draft_001",
  branch: "baseline",
  seeds: 5,
  horizonMonths: 12,
  agentCount: 500,
  runtimeTier: "draft",
  evidenceMode: "fixture-only",
  validationGates: false,
  kpis: ["happiness", "health", "meaning"],
  shocks: ["none"],
  draft: true,
};

export const STANDARD_RUN_SPEC: RunSpec = {
  id: "run_standard_001",
  branch: "baseline",
  seeds: 25,
  horizonMonths: 120,
  agentCount: 5000,
  runtimeTier: "standard",
  evidenceMode: "pack-default",
  validationGates: true,
  kpis: ["happiness", "health", "meaning", "relationships", "financial"],
  shocks: ["labor-market-softening"],
  draft: false,
};

export const DEFAULT_INVALIDATIONS: InvalidatedArtifact[] = [
  {
    id: "population_snapshot:pop_young_adult_5000",
    stage: "Population",
    reason: "Branch membership changes the target population hash.",
    regenerationCost: "45s synth + 12MB artifact",
  },
  {
    id: "simulation_run:run_standard_001",
    stage: "Execute",
    reason: "Seeds, shocks, or horizon changed after the run artifact was created.",
    regenerationCost: "2m 10s runtime + 34MB artifact",
  },
  {
    id: "validation_report:validation_v0",
    stage: "Validate",
    reason: "Validation metrics depend on the run output sequence.",
    regenerationCost: "35s validation",
  },
  {
    id: "brief:published_candidate",
    stage: "Brief",
    reason: "Published findings cannot point at stale validation artifacts.",
    regenerationCost: "Manual review required",
  },
];

export function applyDraftMode(enabled: boolean, current: RunSpec): RunSpec {
  if (!enabled) {
    return {
      ...STANDARD_RUN_SPEC,
      branch: current.branch,
      kpis: current.kpis,
      shocks: current.shocks,
    };
  }
  return {
    ...current,
    seeds: 5,
    horizonMonths: 12,
    agentCount: 500,
    runtimeTier: "draft",
    evidenceMode: "fixture-only",
    validationGates: false,
    draft: true,
  };
}
