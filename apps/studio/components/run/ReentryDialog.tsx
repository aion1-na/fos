"use client";

import { useEffect, useState } from "react";

import type { InvalidatedArtifact } from "@/lib/run/types";

export function ReentryDialog({
  artifacts,
  open,
  onCancel,
  onConfirm,
  proposedEdit,
  scenarioId = "scenario-default",
}: {
  artifacts: InvalidatedArtifact[];
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
  proposedEdit?: { field: string; value: string | number | boolean | string[] };
  scenarioId?: string;
}) {
  const [previewArtifacts, setPreviewArtifacts] = useState<InvalidatedArtifact[]>(artifacts);

  useEffect(() => {
    if (!open) {
      return;
    }
    if (!proposedEdit) {
      setPreviewArtifacts(artifacts);
      return;
    }
    const controller = new AbortController();
    fetch(`/scenarios/${scenarioId}/invalidation-preview`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(proposedEdit),
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("preview unavailable");
        }
        return response.json() as Promise<{ invalidated_artifacts: InvalidatedArtifact[] }>;
      })
      .then((preview) => setPreviewArtifacts(preview.invalidated_artifacts))
      .catch(() => setPreviewArtifacts(artifacts));
    return () => controller.abort();
  }, [artifacts, open, proposedEdit, scenarioId]);

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
          {previewArtifacts.map((artifact) => (
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
