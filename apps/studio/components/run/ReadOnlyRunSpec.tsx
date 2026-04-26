import { formatRunSpecRows } from "@/lib/run/format";
import type { RunSpec } from "@/lib/run/types";

export function ReadOnlyRunSpec({ spec }: { spec: RunSpec }) {
  return (
    <section className="run-panel" aria-label="Read-only run parameters">
      <header>
        <p className="eyebrow">Run Parameters</p>
        <h2>Locked configuration</h2>
      </header>
      <dl className="field-list">
        {formatRunSpecRows(spec).map((row) => (
          <div className="field-row" key={row.label}>
            <dt>{row.label}</dt>
            <dd>{row.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
