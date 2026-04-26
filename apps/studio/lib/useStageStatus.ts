"use client";

import type { Stage } from "./stages";

export type StageStatus = "empty" | "pending" | "ready";

export function useStageStatus(): Record<Stage, StageStatus> {
  return {
    frame: "ready",
    compose: "pending",
    evidence: "empty",
    population: "empty",
    configure: "empty",
    execute: "empty",
    validate: "empty",
    explore: "empty",
    brief: "empty",
  };
}
