"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { STAGES, stageTitle, type Stage } from "@/lib/stages";
import { useStageStatus } from "@/lib/useStageStatus";

export function StageRail() {
  const params = useParams<{ stage?: Stage }>();
  const activeStage = params.stage ?? "frame";
  const statuses = useStageStatus();

  return (
    <aside className="stage-rail" aria-label="Studio stages">
      <p className="brand">FOS Studio</p>
      <nav className="rail-list">
        {STAGES.map((stage) => (
          <Link
            aria-current={activeStage === stage ? "page" : undefined}
            className="rail-link"
            data-active={activeStage === stage}
            href={`/studio/${stage}`}
            key={stage}
          >
            <span
              aria-label={`${statuses[stage]} status`}
              className="status-dot"
              data-status={statuses[stage]}
            />
            <span>{stageTitle(stage)}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
}
