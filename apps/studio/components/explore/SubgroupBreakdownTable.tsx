import type { CausalTracePayload } from "@/lib/validation/types";

export function SubgroupBreakdownTable({
  subgroups,
}: {
  subgroups: CausalTracePayload["subgroups"];
}) {
  return (
    <section className="run-panel">
      <h2>Subgroup Breakdown</h2>
      <div className="claim-table">
        <div className="claim-row claim-header">
          <span>Subgroup</span>
          <span>N</span>
          <span>Effect</span>
          <span>CI</span>
        </div>
        {subgroups.map((subgroup) => (
          <div className="claim-row" key={subgroup.label}>
            <span>{subgroup.label}</span>
            <span>{subgroup.n.toLocaleString()}</span>
            <span>{subgroup.effect.toFixed(2)}</span>
            <span>
              [{subgroup.ci[0].toFixed(2)}, {subgroup.ci[1].toFixed(2)}]
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
