import { BriefExportGate } from "@/components/validation/BriefExportGate";
import { CausalTraceDecomposition } from "@/components/validation/CausalTraceDecomposition";
import { ClaimGateTable } from "@/components/validation/ClaimGateTable";
import { FindingSaveButton } from "@/components/validation/FindingSaveButton";
import { RUN_ID, causalTraceFixture, validationFixture } from "@/lib/validation/fixture";

export default function ValidatePage() {
  const redGate = validationFixture.headline_claims.some((claim) => claim.gate === "red");

  return (
    <main className="workspace run-workspace">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 7</p>
        <h1>Validate</h1>
        <p className="summary-line">
          Trust wedge for headline causal claims, distributional fidelity, stability, drift, and export gates.
        </p>
      </header>
      <div className="run-grid">
        <div className="run-column">
          <ClaimGateTable claims={validationFixture.headline_claims} />
          <CausalTraceDecomposition pathways={causalTraceFixture.pathways} />
        </div>
        <div className="run-column">
          <BriefExportGate blocked={redGate || validationFixture.brief_export_blocked} runId={RUN_ID} />
          <section className="run-panel">
            <h2>Saved Finding Artifact</h2>
            <p className="summary-line">Findings are artifacts referenced by Brief, not free-text notes.</p>
            <FindingSaveButton
              artifactRefs={[validationFixture.report_id, "causal_trace:run_standard_001"]}
              claim={validationFixture.headline_claims[0].claim}
              runId={RUN_ID}
              source="validate"
              title="Validation-supported relationship stability finding"
            />
          </section>
        </div>
      </div>
    </main>
  );
}
