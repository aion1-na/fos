import type { HeadlineClaim } from "@/lib/validation/types";

export function ClaimGateTable({ claims }: { claims: HeadlineClaim[] }) {
  return (
    <section className="run-panel">
      <h2>Headline Causal Claims</h2>
      <div className="claim-table" role="table">
        <div className="claim-row claim-header" role="row">
          <span>Claim</span>
          <span>E-value</span>
          <span>Fidelity</span>
          <span>Seed variance</span>
          <span>Drift</span>
          <span>Gate</span>
        </div>
        {claims.map((claim) => (
          <div className="claim-row" key={claim.id} role="row">
            <span>{claim.claim}</span>
            <span>{claim.e_value.toFixed(2)}</span>
            <span>
              <span className="status-badge" data-status={claim.distributional_fidelity.status}>
                {claim.distributional_fidelity.status}
              </span>{" "}
              KS {claim.distributional_fidelity.ks.toFixed(3)}
            </span>
            <span>{claim.seed_stability_variance.toFixed(3)}</span>
            <span>
              <span className="status-badge" data-status={claim.drift_status}>
                {claim.drift_status}
              </span>
            </span>
            <span>
              <span className="status-badge" data-status={claim.gate}>
                {claim.gate}
              </span>
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
