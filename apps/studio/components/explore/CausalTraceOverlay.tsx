import type { CausalPathway } from "@/lib/validation/types";

export function CausalTraceOverlay({ pathways }: { pathways: CausalPathway[] }) {
  return (
    <section className="run-panel">
      <h2>Causal Trace Overlay</h2>
      <div className="trace-overlay">
        {pathways.map((pathway, index) => (
          <span
            data-calibrated={pathway.calibrated}
            key={pathway.id}
            style={{ left: `${8 + index * 22}%`, top: `${48 - pathway.shapley_value * 80}%` }}
          >
            {pathway.label}
          </span>
        ))}
      </div>
    </section>
  );
}
