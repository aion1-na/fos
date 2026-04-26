"use client";

import { useState } from "react";

import { OverrideDialog } from "@/components/validation/OverrideDialog";
import type { OverrideRecord } from "@/lib/validation/overrides";

export function BriefExportGate({
  blocked,
  runId,
}: {
  blocked: boolean;
  runId: string;
}) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [override, setOverride] = useState<OverrideRecord | null>(null);

  if (!blocked || override) {
    return (
      <section className="run-panel">
        <h2>Brief Export Gate</h2>
        <p className="summary-line">Brief export is available for {runId}.</p>
        {override ? (
          <div className="audit-entry">
            <strong>{override.audit_event}</strong>
            <p>{override.justification}</p>
          </div>
        ) : null}
      </section>
    );
  }

  return (
    <section className="run-panel red-gate-panel">
      <h2>Brief Export Blocked</h2>
      <p className="summary-line">
        A red validation gate blocks brief export by default. Override requires written justification and is recorded
        in the run artifact, audit log, and brief assumptions.
      </p>
      <button className="primary-button" onClick={() => setDialogOpen(true)} type="button">
        Override amber gate
      </button>
      <OverrideDialog
        gate="amber"
        onCancel={() => setDialogOpen(false)}
        onRecorded={(record) => {
          setOverride(record);
          setDialogOpen(false);
        }}
        open={dialogOpen}
        runId={runId}
      />
    </section>
  );
}
