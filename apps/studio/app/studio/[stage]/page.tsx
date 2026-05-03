import { notFound } from "next/navigation";

import { graphStudioInterventionPriors } from "@/lib/evidence/interventionPriors";
import { STAGES, isStage, stageTitle, type Stage } from "@/lib/stages";

type StagePageProps = {
  params: {
    stage: string;
  };
};

export function generateStaticParams(): Array<{ stage: Stage }> {
  return STAGES.map((stage) => ({ stage }));
}

export default function StagePage({ params }: StagePageProps) {
  if (!isStage(params.stage)) {
    notFound();
  }

  const title = stageTitle(params.stage);
  const isEvidenceStage = params.stage === "evidence";

  return (
    <main className="workspace" id="studio-main">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage</p>
        <h1>{title}</h1>
      </header>
      {isEvidenceStage ? (
        <section className="placeholder-panel" aria-label="FOS Graph Studio forest-plot view">
          <h2>Intervention prior forest plot</h2>
          <p>
            Fixture-only request-status priors are visual context for review. Graph layout does not
            create evidence or causal effect sizes.
          </p>
          <div className="evidence-prior-list">
            {graphStudioInterventionPriors.map((claim) => (
              <div className="evidence-prior-row" key={claim.claimId}>
                <strong>{claim.scenarioId}</strong>
                <span>{claim.outcomeDomain}</span>
                <span>{claim.effectSize.toFixed(2)}</span>
                <span>{claim.ciLow.toFixed(2)} to {claim.ciHigh.toFixed(2)}</span>
                <span>{claim.reviewStatus}</span>
                <span>causal effect validated: {String(claim.causalEffectValidated)}</span>
              </div>
            ))}
          </div>
        </section>
      ) : (
        <section className="placeholder-panel" aria-label={`${title} placeholder`}>
          <h2>{title} Placeholder</h2>
          <p>This stage shell is intentionally empty until workflow behavior is defined.</p>
        </section>
      )}
    </main>
  );
}
