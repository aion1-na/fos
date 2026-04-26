"use client";

import type { AgentRecord } from "@/lib/population/types";

export function AgentDrawer({
  agent,
  onClose,
}: {
  agent: AgentRecord | null;
  onClose: () => void;
}) {
  if (!agent) {
    return null;
  }

  return (
    <aside className="agent-drawer" aria-label="Agent inspector">
      <div className="drawer-header">
        <div>
          <p className="eyebrow">Agent</p>
          <h2>{agent.id}</h2>
        </div>
        <button className="icon-button" type="button" onClick={onClose} aria-label="Close agent inspector">
          x
        </button>
      </div>
      <dl className="field-list">
        {Object.entries(agent.fields).map(([key, value]) => (
          <div className="field-row" key={key}>
            <dt>{key.replaceAll("_", " ")}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}
