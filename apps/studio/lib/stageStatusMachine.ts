import type { Stage } from "@/lib/stages";

export type StageStatus = "empty" | "pending" | "ready" | "running" | "complete" | "error";

export type StageStatusRow = {
  id: string;
  from: StageStatus;
  event: string;
  to: StageStatus;
};

export const STAGE_STATUS_ROWS: StageStatusRow[] = [
  { id: "8.4.1-empty-edit", from: "empty", event: "upstream_edit", to: "pending" },
  { id: "8.4.1-pending-save", from: "pending", event: "artifact_saved", to: "ready" },
  { id: "8.4.1-ready-start", from: "ready", event: "run_started", to: "running" },
  { id: "8.4.1-running-complete", from: "running", event: "run_completed", to: "complete" },
  { id: "8.4.1-running-fail", from: "running", event: "run_failed", to: "error" },
  { id: "8.4.1-error-retry", from: "error", event: "retry_requested", to: "pending" },
  { id: "8.4.1-complete-upstream", from: "complete", event: "upstream_edit", to: "pending" },
  { id: "8.4.1-ready-upstream", from: "ready", event: "upstream_edit", to: "pending" },
];

export function transitionStageStatus(
  from: StageStatus,
  event: string,
): StageStatus {
  return STAGE_STATUS_ROWS.find((row) => row.from === from && row.event === event)?.to ?? from;
}

export function defaultStageStatuses(): Record<Stage, StageStatus> {
  return {
    frame: "ready",
    compose: "pending",
    evidence: "empty",
    population: "ready",
    configure: "ready",
    execute: "pending",
    validate: "empty",
    explore: "empty",
    brief: "empty",
  };
}
