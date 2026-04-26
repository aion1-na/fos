"use client";

import type { InvalidatedArtifact } from "@/lib/run/types";

export function ReentryDialog({
  artifacts,
  open,
  onCancel,
  onConfirm,
}: {
  artifacts: InvalidatedArtifact[];
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  if (!open) {
    return null;
  }

  return (
    <div className="modal-scrim" role="presentation">
      <section aria-modal="true" className="reentry-dialog" role="dialog">
        <header>
          <p className="eyebrow">Controlled Re-entry</p>
          <h2>Regenerate downstream artifacts first</h2>
        </header>
        <div className="artifact-list">
          {artifacts.map((artifact) => (
            <article className="artifact-row" key={artifact.id}>
              <div>
                <strong>{artifact.id}</strong>
                <p>{artifact.stage} · {artifact.reason}</p>
              </div>
              <span>{artifact.regenerationCost}</span>
            </article>
          ))}
        </div>
        <footer className="dialog-actions">
          <button className="secondary-button" type="button" onClick={onCancel}>
            Cancel
          </button>
          <button className="primary-button" type="button" onClick={onConfirm}>
            Regenerate and continue
          </button>
        </footer>
      </section>
    </div>
  );
}
