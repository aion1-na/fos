"use client";

import { useState } from "react";

import { ReadOnlyRunSpec } from "@/components/run/ReadOnlyRunSpec";
import { ReentryDialog } from "@/components/run/ReentryDialog";
import { RunConsoleStream } from "@/components/run/RunConsoleStream";
import { DEFAULT_INVALIDATIONS, STANDARD_RUN_SPEC } from "@/lib/run/types";

function UpstreamEditGuard() {
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <button className="secondary-button" type="button" onClick={() => setDialogOpen(true)}>
        Upstream edit
      </button>
      <ReentryDialog
        artifacts={DEFAULT_INVALIDATIONS}
        open={dialogOpen}
        onCancel={() => setDialogOpen(false)}
        onConfirm={() => setDialogOpen(false)}
        proposedEdit={{ field: "execute_upstream_edit", value: "requested" }}
      />
    </>
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
      <div className="run-footer execute-toolbar">
        <span>Execution accepts saved specs only.</span>
        <UpstreamEditGuard />
      </div>
      <div className="run-grid execute-grid">
        <ReadOnlyRunSpec spec={STANDARD_RUN_SPEC} />
        <RunConsoleStream simulationId={STANDARD_RUN_SPEC.id} />
      </div>
    </main>
  );
}
