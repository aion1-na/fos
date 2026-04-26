"use client";

export type KpiTickFrame = {
  offset: number;
  tick: number;
  kpis: Record<string, number>;
};

export function KpiTraceChart({ ticks }: { ticks: KpiTickFrame[] }) {
  const latest = ticks.at(-1);
  const values = ticks.map((tick) => tick.kpis.happiness ?? 0);
  const max = Math.max(...values, 1);

  return (
    <section className="run-panel">
      <h2>KPI Trace Chart</h2>
      <div className="kpi-trace" aria-label="KPI trace chart">
        {values.map((value, index) => (
          <span
            className="kpi-bar"
            key={`${index}-${value}`}
            style={{ height: `${Math.max(6, (value / max) * 86)}px` }}
          />
        ))}
      </div>
      <p className="summary-line">
        Latest happiness: {latest ? latest.kpis.happiness.toFixed(3) : "waiting"}
      </p>
    </section>
  );
}
