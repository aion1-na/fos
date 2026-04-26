import { notFound } from "next/navigation";

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

  return (
    <main className="workspace">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage</p>
        <h1>{title}</h1>
      </header>
      <section className="placeholder-panel" aria-label={`${title} placeholder`}>
        <h2>{title} Placeholder</h2>
        <p>This stage shell is intentionally empty until workflow behavior is defined.</p>
      </section>
    </main>
  );
}
