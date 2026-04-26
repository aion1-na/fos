"use client";

import type { Stage } from "./stages";
import { defaultStageStatuses, type StageStatus } from "./stageStatusMachine";

export type { StageStatus };

export function useStageStatus(): Record<Stage, StageStatus> {
  return defaultStageStatuses();
}
