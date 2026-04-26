import type { CausalTracePayload } from "@/lib/validation/types";

export function UnintendedConsequenceList({
  items,
}: {
  items: CausalTracePayload["unintended_consequences"];
}) {
  return (
    <section className="run-panel">
      <h2>Unintended Consequences</h2>
      <div className="artifact-list">
        {items.map((item) => (
          <article className="artifact-row" key={item.label}>
            <div>
              <strong>{item.label}</strong>
              <p>{item.note}</p>
            </div>
            <span className="status-badge" data-status={item.severity}>
              {item.severity}
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}
