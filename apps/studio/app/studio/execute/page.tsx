"use client";

import { useState } from "react";

import { ReadOnlyRunSpec } from "@/components/run/ReadOnlyRunSpec";
import { ReentryDialog } from "@/components/run/ReentryDialog";
import { DEFAULT_INVALIDATIONS, STANDARD_RUN_SPEC } from "@/lib/run/types";

function RunConsole() {
  const [status, setStatus] = useState<"idle" | "queued" | "running" | "complete">("idle");
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <section className="run-panel console-panel">
      <header>
        <p className="eyebrow">Run Console</p>
        <h2>Execution queue</h2>
      </header>
      <ol className="console-log">
        <li data-state="complete">Loaded saved run spec</li>
        <li data-state={status === "idle" ? "pending" : "complete"}>Reserved runtime worker</li>
        <li data-state={status === "complete" ? "complete" : "pending"}>Wrote run artifact manifest</li>
      </ol>
      <div className="console-actions">
        <button className="secondary-button" type="button" onClick={() => setDialogOpen(true)}>
          Upstream edit
        </button>
        <button
          className="primary-button"
          type="button"
          onClick={() => {
            setStatus("queued");
            window.setTimeout(() => setStatus("running"), 150);
            window.setTimeout(() => setStatus("complete"), 450);
          }}
        >
          Start run
        </button>
      </div>
      <p className="summary-line">Status: {status}</p>
      <ReentryDialog
        artifacts={DEFAULT_INVALIDATIONS}
        open={dialogOpen}
        onCancel={() => setDialogOpen(false)}
        onConfirm={() => setDialogOpen(false)}
      />
    </section>
  );
}

export default function ExecutePage() {
  return (
    <main className="workspace run-workspace">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 6</p>
        <h1>Execute</h1>
        <p className="summary-line">Run Console executes a saved spec. Parameters are read-only here.</p>
      </header>
      <div className="run-grid execute-grid">
        <ReadOnlyRunSpec spec={STANDARD_RUN_SPEC} />
        <RunConsole />
      </div>
    </main>
  );
}
