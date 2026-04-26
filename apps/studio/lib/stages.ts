export const STAGES = [
  "frame",
  "compose",
  "evidence",
  "population",
  "configure",
  "execute",
  "validate",
  "explore",
  "brief",
] as const;

export type Stage = (typeof STAGES)[number];

export function isStage(value: string): value is Stage {
  return STAGES.includes(value as Stage);
}

export function stageTitle(stage: Stage): string {
  return stage.charAt(0).toUpperCase() + stage.slice(1);
}
