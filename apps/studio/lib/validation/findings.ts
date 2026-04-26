import type { SavedFinding } from "@/lib/validation/types";

export async function saveFinding(
  runId: string,
  finding: Omit<SavedFinding, "id" | "run_id">,
): Promise<SavedFinding> {
  const response = await fetch(`/runs/${runId}/findings`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(finding),
  }).catch(() => null);
  if (response?.ok) {
    return (await response.json()) as SavedFinding;
  }
  return {
    id: `finding_local_${runId}`,
    run_id: runId,
    ...finding,
  };
}
