"use client";

import { useEffect, useMemo, useRef } from "react";
import { buildInstancedWorld } from "@fos/render-core";

import type { PopulationInspectorData } from "@/lib/population/types";

export function WorldRenderer({
  population,
  enabled,
}: {
  population: PopulationInspectorData;
  enabled: boolean;
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const world = useMemo(
    () =>
      buildInstancedWorld(
        population.agents.map((agent) => ({
          id: agent.id,
          institutionId: agent.institutionId,
        })),
        population.institutions,
      ),
    [population],
  );

  useEffect(() => {
    if (!enabled || !canvasRef.current) {
      return;
    }
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");
    if (!context) {
      return;
    }
    const ratio = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = Math.floor(rect.width * ratio);
    canvas.height = Math.floor(rect.height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, rect.width, rect.height);
    context.fillStyle = "#f4f7f3";
    context.fillRect(0, 0, rect.width, rect.height);

    for (const building of world.institutions) {
      context.fillStyle = building.color;
      context.globalAlpha = 0.24;
      context.fillRect(
        building.x * rect.width,
        building.y * rect.height,
        building.width * rect.width,
        building.height * rect.height,
      );
      context.globalAlpha = 1;
      context.fillStyle = "#26312d";
      context.font = "11px system-ui";
      context.fillText(building.label, building.x * rect.width, building.y * rect.height + 12);
    }

    for (const agent of world.agents) {
      context.fillStyle = agent.color;
      context.fillRect(agent.x * rect.width, 70 + agent.y * (rect.height - 82), agent.size, agent.size);
    }
  }, [enabled, world]);

  if (!enabled) {
    return (
      <div className="world-placeholder">
        <p>World renderer is off</p>
      </div>
    );
  }

  return (
    <div className="world-frame">
      <canvas ref={canvasRef} aria-label="Population world renderer" />
      <span className="frame-budget">target &lt; {world.budgetMsPerFrame}ms/frame at 5K agents</span>
    </div>
  );
}
