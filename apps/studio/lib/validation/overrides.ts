export type OverrideRecord = {
  id: string;
  run_id: string;
  gate: string;
  justification: string;
  assumptions: string[];
  audit_event: string;
};

export const OVERRIDE_STORAGE_KEY = "fos.validation.overrides";

function stableId(runId: string, gate: string, justification: string): string {
  let hash = 0;
  for (const char of `${runId}:${gate}:${justification}`) {
    hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  }
  return `override_${hash.toString(16).padStart(8, "0")}`;
}

export function readOverrides(): OverrideRecord[] {
  if (typeof window === "undefined") {
    return [];
  }
  const raw = window.localStorage.getItem(OVERRIDE_STORAGE_KEY);
  if (!raw) {
    return [];
  }
  try {
    const parsed = JSON.parse(raw) as OverrideRecord[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function recordOverride(
  runId: string,
  gate: string,
  justification: string,
): OverrideRecord {
  const override: OverrideRecord = {
    id: stableId(runId, gate, justification),
    run_id: runId,
    gate,
    justification,
    assumptions: [`Privileged validation override for ${gate}: ${justification}`],
    audit_event: "validation_gate_override_recorded",
  };
  const existing = readOverrides().filter((record) => record.id !== override.id);
  window.localStorage.setItem(OVERRIDE_STORAGE_KEY, JSON.stringify([...existing, override]));
  return override;
}

export function overridesForRun(runId: string): OverrideRecord[] {
  return readOverrides().filter((override) => override.run_id === runId);
}
