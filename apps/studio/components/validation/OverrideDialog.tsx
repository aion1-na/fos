"use client";

import { useState } from "react";

import { recordOverride, type OverrideRecord } from "@/lib/validation/overrides";

export function OverrideDialog({
  gate,
  onCancel,
  onRecorded,
  open,
  runId,
}: {
  gate: string;
  onCancel: () => void;
  onRecorded: (override: OverrideRecord) => void;
  open: boolean;
  runId: string;
}) {
  const [justification, setJustification] = useState("");

  if (!open) {
    return null;
  }

  const trimmed = justification.trim();
  const valid = trimmed.length >= 50;

  return (
    <div className="modal-scrim" role="presentation">
      <section aria-modal="true" className="reentry-dialog" role="dialog">
        <header>
          <p className="eyebrow">Privileged Override</p>
          <h2>Override {gate} validation gate</h2>
        </header>
        <p className="summary-line">
          Justification must be at least 50 characters. The override is stored in the run artifact, audit log, and
          Brief assumptions for this run only.
        </p>
        <label className="stacked-field">
          Written justification
          <textarea
            onChange={(event) => setJustification(event.target.value)}
            placeholder="Explain why this validation gate can be overridden for this run."
            value={justification}
          />
        </label>
        <footer className="dialog-actions">
          <button className="secondary-button" type="button" onClick={onCancel}>
            Cancel
          </button>
          <button
            className="primary-button"
            disabled={!valid}
            onClick={async () => {
              await fetch(`/runs/${runId}/overrides`, {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ gate, justification: trimmed }),
              }).catch(() => null);
              onRecorded(recordOverride(runId, gate, trimmed));
            }}
            type="button"
          >
            Submit override
          </button>
        </footer>
      </section>
    </div>
  );
}
