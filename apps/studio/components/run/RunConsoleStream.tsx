"use client";

import { useMemo, useState } from "react";

import { EventLogTail, type EventLogFrame } from "@/components/run/EventLogTail";
import { KpiTraceChart, type KpiTickFrame } from "@/components/run/KpiTraceChart";

type AgentUpdateFrame = {
  offset: number;
  tick: number;
  count: number;
};

type StreamFrame =
  | ({ type: "agent_update_count" } & AgentUpdateFrame)
  | ({ type: "event_log_entry" } & EventLogFrame)
  | ({ type: "kpi_tick" } & KpiTickFrame);

const FIXTURE_FRAMES: StreamFrame[] = Array.from({ length: 12 }, (_, tick) => tick).flatMap((tick) => [
  { type: "agent_update_count", offset: tick * 3, tick, count: 500 + tick * 37 },
  { type: "event_log_entry", offset: tick * 3 + 1, tick, message: `Committed tick ${tick}` },
  {
    type: "kpi_tick",
    offset: tick * 3 + 2,
    tick,
    kpis: {
      happiness: Number((0.55 + tick * 0.004).toFixed(4)),
      health: Number((0.61 + tick * 0.002).toFixed(4)),
      meaning: Number((0.58 + tick * 0.003).toFixed(4)),
    },
  },
]);

export function RunConsoleStream({ simulationId }: { simulationId: string }) {
  const [frames, setFrames] = useState<StreamFrame[]>([]);
  const [status, setStatus] = useState<"idle" | "streaming" | "complete">("idle");

  const agentUpdates = useMemo(
    () => frames.filter((frame): frame is { type: "agent_update_count" } & AgentUpdateFrame => frame.type === "agent_update_count"),
    [frames],
  );
  const eventFrames = useMemo(
    () => frames.filter((frame): frame is { type: "event_log_entry" } & EventLogFrame => frame.type === "event_log_entry"),
    [frames],
  );
  const kpiFrames = useMemo(
    () => frames.filter((frame): frame is { type: "kpi_tick" } & KpiTickFrame => frame.type === "kpi_tick"),
    [frames],
  );

  function startFixtureStream() {
    setStatus("streaming");
    setFrames([]);
    FIXTURE_FRAMES.forEach((frame, index) => {
      window.setTimeout(() => {
        setFrames((current) => [...current, frame]);
        if (index === FIXTURE_FRAMES.length - 1) {
          setStatus("complete");
        }
      }, index * 20);
    });
  }

  const latestAgentCount = agentUpdates.at(-1)?.count ?? 0;

  return (
    <div className="run-stream-stack">
      <section className="run-panel console-panel">
        <header>
          <p className="eyebrow">Run Console Stream</p>
          <h2>{simulationId}</h2>
        </header>
        <div className="compact-list">
          <div>
            <dt>Status</dt>
            <dd>{status}</dd>
          </div>
          <div>
            <dt>Frames</dt>
            <dd>{frames.length}</dd>
          </div>
          <div>
            <dt>Agent updates</dt>
            <dd>{latestAgentCount.toLocaleString()}</dd>
          </div>
        </div>
        <div className="console-actions">
          <button className="primary-button" type="button" onClick={startFixtureStream}>
            Start run
          </button>
        </div>
      </section>
      <EventLogTail events={eventFrames} />
      <KpiTraceChart ticks={kpiFrames} />
    </div>
  );
}
