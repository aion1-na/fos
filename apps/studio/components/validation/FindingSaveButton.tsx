"use client";

import { useState } from "react";

import { saveFinding } from "@/lib/validation/findings";
import type { SavedFinding } from "@/lib/validation/types";

export function FindingSaveButton({
  artifactRefs,
  claim,
  runId,
  source,
  title,
}: {
  artifactRefs: string[];
  claim: string;
  runId: string;
  source: "validate" | "explore";
  title: string;
}) {
  const [finding, setFinding] = useState<SavedFinding | null>(null);

  return (
    <div className="finding-save">
      <button
        className="secondary-button"
        onClick={async () =>
          setFinding(
            await saveFinding(runId, {
              title,
              claim,
              source,
              artifact_refs: artifactRefs,
              assumptions: source === "validate" ? ["Validation gates reviewed"] : ["Exploratory finding"],
              override: null,
            }),
          )
        }
        type="button"
      >
        Save finding
      </button>
      {finding ? <span>Saved {finding.id}</span> : null}
    </div>
  );
}
