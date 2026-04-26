import type { CausalPathway } from "@/lib/validation/types";

export function CausalTraceDecomposition({ pathways }: { pathways: CausalPathway[] }) {
  return (
    <section className="run-panel">
      <h2>Shapley Pathway Decomposition</h2>
      <div className="pathway-list">
        {pathways.map((pathway) => (
          <article className="pathway-row" data-calibrated={pathway.calibrated} key={pathway.id}>
            <div>
              <strong>{pathway.label}</strong>
              <p>
                {pathway.calibrated
                  ? `Cited evidence claim id: ${pathway.evidence_claim_id}`
                  : "Exploratory pathway: no calibrated evidence claim"}
              </p>
            </div>
            <div className="pathway-bar">
              <span style={{ width: `${Math.max(4, pathway.shapley_value * 100)}%` }} />
            </div>
            <span>
              {pathway.shapley_value.toFixed(2)} [{pathway.confidence_interval[0].toFixed(2)},{" "}
              {pathway.confidence_interval[1].toFixed(2)}]
            </span>
          </article>
        ))}
      </div>
    </section>
  );
}
