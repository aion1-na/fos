import type { CausalTracePayload } from "@/lib/validation/types";

export function RepresentativeAgentPanel({
  agent,
}: {
  agent: CausalTracePayload["representative_agent"];
}) {
  return (
    <section className="run-panel">
      <h2>Representative Agent</h2>
      <p className="summary-line">{agent.id}</p>
      <p>{agent.summary}</p>
    </section>
  );
}
