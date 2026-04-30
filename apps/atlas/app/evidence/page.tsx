import { evidenceClaims } from "@/lib/evidence/claims";

export default function EvidencePage() {
  const plottedClaims = evidenceClaims
    .filter((claim) => claim.reviewStatus !== "rejected")
    .slice(0, 36);
  const statusCounts = evidenceClaims.reduce<Record<string, number>>((counts, claim) => {
    counts[claim.reviewStatus] = (counts[claim.reviewStatus] ?? 0) + 1;
    return counts;
  }, {});

  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Evidence forest plot</h1>
        <p className="lede">
          Intervention priors with risk-of-bias, confidence labels, and claim-to-provenance traceability.
        </p>
      </header>

      <section className="dataset-grid" aria-label="Curator review status">
        {["draft", "advisor_reviewed", "rejected", "superseded"].map((status) => (
          <article className="dataset-card" key={status}>
            <h2>{status}</h2>
            <p className="lede">{statusCounts[status] ?? 0} evidence claims</p>
          </article>
        ))}
      </section>

      <section className="dataset-card forest-plot" aria-label="Atlas forest-plot view for intervention priors">
        <h2>Forest plot</h2>
        <div className="forest-axis" aria-hidden="true">
          <span>-0.10</span>
          <span>0</span>
          <span>0.30</span>
        </div>
        {plottedClaims.map((claim) => {
          const left = Math.max(0, Math.min(100, ((claim.ciLow + 0.1) / 0.4) * 100));
          const right = Math.max(0, Math.min(100, ((claim.ciHigh + 0.1) / 0.4) * 100));
          const point = Math.max(0, Math.min(100, ((claim.effectSize + 0.1) / 0.4) * 100));

          return (
            <div className="forest-row" key={claim.claimId}>
              <div>
                <strong>{claim.scenarioId}</strong>
                <span>{claim.outcomeDomain}</span>
              </div>
              <div className="forest-line">
                <span className="forest-ci" style={{ left: `${left}%`, width: `${right - left}%` }} />
                <span className="forest-point" style={{ left: `${point}%` }} data-status={claim.reviewStatus} />
              </div>
              <span>{claim.effectSize.toFixed(2)}</span>
            </div>
          );
        })}
      </section>

      <section className="dataset-card" aria-label="Intervention effect size priors">
        <h2>Effect size priors</h2>
        <table>
          <thead>
            <tr>
              <th>Claim</th>
              <th>Transition</th>
              <th>Population</th>
              <th>Treatment</th>
              <th>Comparator</th>
              <th>Outcome</th>
              <th>Estimate</th>
              <th>Uncertainty</th>
              <th>Risk of bias</th>
              <th>Transport</th>
              <th>Confidence</th>
              <th>Status</th>
              <th>Trace</th>
            </tr>
          </thead>
          <tbody>
            {evidenceClaims.slice(0, 60).map((claim) => (
              <tr key={claim.claimId}>
                <td>{claim.claimId}</td>
                <td>{claim.transitionModelId}</td>
                <td>{claim.targetPopulation}</td>
                <td>{claim.treatment}</td>
                <td>{claim.comparator}</td>
                <td>{claim.outcomeDomain}</td>
                <td>{claim.effectSize.toFixed(2)}</td>
                <td>{claim.uncertainty.toFixed(2)}</td>
                <td>{claim.riskOfBias}</td>
                <td>{claim.transportability}</td>
                <td>{claim.confidenceLabel}</td>
                <td>{claim.reviewStatus}</td>
                <td>
                  {claim.sourceId} {"->"} {claim.datasetCard} {"->"} {claim.provenanceManifest}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
