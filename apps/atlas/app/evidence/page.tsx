import { evidenceClaims } from "@/lib/evidence/claims";

export default function EvidencePage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">Atlas</p>
        <h1>Evidence forest plot</h1>
        <p className="lede">
          Intervention priors with risk-of-bias, confidence labels, and claim-to-provenance traceability.
        </p>
      </header>

      <section className="dataset-card" aria-label="Intervention effect size priors">
        <h2>Effect size priors</h2>
        <table>
          <thead>
            <tr>
              <th>Claim</th>
              <th>Treatment</th>
              <th>Outcome</th>
              <th>Estimate</th>
              <th>Uncertainty</th>
              <th>Risk of bias</th>
              <th>Confidence</th>
              <th>Trace</th>
            </tr>
          </thead>
          <tbody>
            {evidenceClaims.map((claim) => (
              <tr key={claim.claimId}>
                <td>{claim.claimId}</td>
                <td>{claim.treatment}</td>
                <td>{claim.outcome}</td>
                <td>{claim.estimate.toFixed(2)}</td>
                <td>{claim.uncertainty.toFixed(2)}</td>
                <td>{claim.riskOfBias}</td>
                <td>{claim.confidenceLabel}</td>
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
