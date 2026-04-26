import { BranchViewer } from "@/components/explore/BranchViewer";
import { CausalTraceOverlay } from "@/components/explore/CausalTraceOverlay";
import { RepresentativeAgentPanel } from "@/components/explore/RepresentativeAgentPanel";
import { SixDomainRadar } from "@/components/explore/SixDomainRadar";
import { SubgroupBreakdownTable } from "@/components/explore/SubgroupBreakdownTable";
import { UnintendedConsequenceList } from "@/components/explore/UnintendedConsequenceList";
import { FindingSaveButton } from "@/components/validation/FindingSaveButton";
import { RUN_ID, causalTraceFixture } from "@/lib/validation/fixture";

export default function ExplorePage() {
  return (
    <main className="workspace run-workspace" id="studio-main">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 8</p>
        <h1>Explore</h1>
        <p className="summary-line">
          Branch comparison, causal traces, subgroup effects, representative agents, and saved finding artifacts.
        </p>
      </header>
      <div className="run-grid">
        <div className="run-column">
          <BranchViewer branches={causalTraceFixture.branches} />
          <CausalTraceOverlay pathways={causalTraceFixture.pathways} />
          <SubgroupBreakdownTable subgroups={causalTraceFixture.subgroups} />
        </div>
        <div className="run-column">
          <SixDomainRadar scores={causalTraceFixture.representative_agent.domain_scores} />
          <UnintendedConsequenceList items={causalTraceFixture.unintended_consequences} />
          <RepresentativeAgentPanel agent={causalTraceFixture.representative_agent} />
          <section className="run-panel">
            <h2>Finding Artifact</h2>
            <FindingSaveButton
              artifactRefs={["causal_trace:run_standard_001", causalTraceFixture.representative_agent.id]}
              claim="Training plus mentoring has the largest modeled branch delta, with exploratory peer pathways flagged."
              runId={RUN_ID}
              source="explore"
              title="Exploratory branch delta finding"
            />
          </section>
        </div>
      </div>
    </main>
  );
}
