import type { CausalTracePayload } from "@/lib/validation/types";

export function BranchViewer({ branches }: { branches: CausalTracePayload["branches"] }) {
  return (
    <section className="run-panel">
      <h2>Branch Viewer</h2>
      <div className="metric-grid">
        {branches.map((branch) => (
          <article className="metric-card" key={branch.id}>
            <h2>{branch.label}</h2>
            <p>Delta {branch.delta >= 0 ? "+" : ""}{branch.delta.toFixed(2)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
