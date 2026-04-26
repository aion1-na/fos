"use client";

import { useEffect, useState } from "react";

import { DRAFT_RUN_SPEC } from "@/lib/run/types";
import { RUN_ID } from "@/lib/validation/fixture";
import { overridesForRun, type OverrideRecord } from "@/lib/validation/overrides";

export default function BriefPage() {
  const selectedRun = DRAFT_RUN_SPEC;
  const [overrides, setOverrides] = useState<OverrideRecord[]>([]);

  useEffect(() => {
    setOverrides(overridesForRun(RUN_ID));
  }, []);

  return (
    <main className="workspace">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 9</p>
        <h1>Brief</h1>
      </header>
      <section className="placeholder-panel" aria-label="Brief draft guard">
        <h2>Published brief unavailable</h2>
        <p>
          Draft runs cannot produce a published brief. Select a non-draft run with validation gates enabled before
          publishing.
        </p>
        <p>Current run: {selectedRun.id}</p>
      </section>
      <section className="run-panel brief-assumptions">
        <h2>Assumptions</h2>
        {overrides.length ? (
          <ul>
            {overrides.flatMap((override) =>
              override.assumptions.map((assumption) => <li key={`${override.id}-${assumption}`}>{assumption}</li>),
            )}
          </ul>
        ) : (
          <p className="summary-line">No validation overrides recorded for {RUN_ID}.</p>
        )}
      </section>
    </main>
  );
}
