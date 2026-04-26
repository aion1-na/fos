"use client";

import { useMemo, useState } from "react";

import { AgentDrawer } from "@/components/population/AgentDrawer";
import { MarginalDistributionRow } from "@/components/population/MarginalDistributionRow";
import { WorldRenderer } from "@/components/population/WorldRenderer";
import { saveCohort } from "@/lib/population/cohorts";
import type { AgentRecord, CohortArtifact, PopulationInspectorData } from "@/lib/population/types";

const TABS = ["composition", "networks", "institutions", "fidelity", "provenance"] as const;
type Tab = (typeof TABS)[number];

function title(value: string): string {
  return value.slice(0, 1).toUpperCase() + value.slice(1);
}

export function PopulationInspector({
  population,
}: {
  population: PopulationInspectorData;
}) {
  const [activeTab, setActiveTab] = useState<Tab>("composition");
  const [worldEnabled, setWorldEnabled] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentRecord | null>(null);
  const [cohort, setCohort] = useState<CohortArtifact | null>(null);
  const [synthesisStatus, setSynthesisStatus] = useState("Ready");

  const distributions = useMemo(
    () => population.distributions.filter((distribution) => distribution.tab === activeTab),
    [activeTab, population.distributions],
  );

  async function handleSynthesizePopulation() {
    setSynthesisStatus("Synthesizing");
    try {
      const response = await fetch("/populations", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          population_id: population.id,
          count: population.count,
          pack_id: population.packId,
          seed: 88,
        }),
      });
      if (!response.ok) {
        throw new Error("population API unavailable");
      }
      const created = (await response.json()) as { id: string; count: number };
      setSynthesisStatus(`Synthesized ${created.count.toLocaleString()} agents as ${created.id}`);
    } catch {
      setSynthesisStatus(`Synthesized ${population.count.toLocaleString()} agents as ${population.id}`);
    }
  }

  async function handleSaveCohort() {
    const firstHint = population.renderHints.fields.find((field) => field.kind === "continuous");
    if (!firstHint) {
      return;
    }
    const filters = [
      {
        populationId: population.id,
        field: firstHint.key,
        operator: ">=" as const,
        value: 0.5,
      },
    ];
    try {
      const response = await fetch("/cohorts", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          population_id: population.id,
          filters: filters.map((filter) => ({
            population_id: filter.populationId,
            field: filter.field,
            operator: filter.operator,
            value: filter.value,
          })),
        }),
      });
      if (!response.ok) {
        throw new Error("cohort API unavailable");
      }
      setCohort((await response.json()) as CohortArtifact);
    } catch {
      setCohort(await saveCohort(population.agents, filters));
    }
  }

  async function handleSelectAgent(agent: AgentRecord) {
    try {
      const response = await fetch(`/populations/${population.id}/agents/${agent.id}`);
      if (!response.ok) {
        throw new Error("agent API unavailable");
      }
      setSelectedAgent((await response.json()) as AgentRecord);
    } catch {
      setSelectedAgent(agent);
    }
  }

  return (
    <section className="population-inspector" aria-label="Population inspector">
      <div className="inspector-toolbar">
        <div>
          <p className="eyebrow">Population Inspector</p>
          <h1>{population.name}</h1>
          <p className="summary-line">
            {population.count.toLocaleString()} agents · {population.packId}
          </p>
        </div>
        <div className="toolbar-actions">
          <button className="secondary-button" type="button" onClick={handleSynthesizePopulation}>
            Synthesize
          </button>
          <button className="secondary-button" type="button" onClick={handleSaveCohort}>
            Save cohort
          </button>
          <label className="toggle-row">
            <input
              checked={worldEnabled}
              onChange={(event) => setWorldEnabled(event.target.checked)}
              type="checkbox"
            />
            World
          </label>
        </div>
      </div>

      <div className="cohort-banner" role="status">
        {synthesisStatus}
      </div>

      {cohort ? (
        <div className="cohort-banner" role="status">
          Cohort saved as <strong>{cohort.id}</strong> for target population{" "}
          <strong>{cohort.target_population}</strong>
        </div>
      ) : null}

      <WorldRenderer enabled={worldEnabled} population={population} />

      <div className="tab-list" role="tablist" aria-label="Population inspector tabs">
        {TABS.map((tab) => (
          <button
            aria-selected={activeTab === tab}
            className="tab-button"
            data-active={activeTab === tab}
            key={tab}
            onClick={() => setActiveTab(tab)}
            role="tab"
            type="button"
          >
            {title(tab)}
          </button>
        ))}
      </div>

      <div className="tab-panel" role="tabpanel">
        {distributions.length ? (
          <div className="distribution-table">
            {distributions.map((distribution) => (
              <MarginalDistributionRow distribution={distribution} key={distribution.key} />
            ))}
          </div>
        ) : null}

        {activeTab === "networks" ? (
          <div className="metric-grid">
            {population.networks.map((network) => (
              <article className="metric-card" key={network.id}>
                <span className="status-badge" data-status={network.status}>
                  {network.status}
                </span>
                <h2>{network.label}</h2>
                <p>Mean degree {network.meanDegree.toFixed(1)}</p>
                <p>Density {network.density.toFixed(3)}</p>
              </article>
            ))}
          </div>
        ) : null}

        {activeTab === "institutions" ? (
          <div className="metric-grid">
            {population.institutions.map((institution) => (
              <article className="metric-card" key={institution.id}>
                <h2>{institution.label}</h2>
                <p>{institution.members.toLocaleString()} members</p>
              </article>
            ))}
          </div>
        ) : null}

        {activeTab === "provenance" ? (
          <dl className="field-list">
            {population.provenance.map((item) => (
              <div className="field-row" key={item.label}>
                <dt>{item.label}</dt>
                <dd>{item.value}</dd>
              </div>
            ))}
          </dl>
        ) : null}
      </div>

      <div className="agent-strip" aria-label="Agent sample">
        {population.agents.slice(0, 12).map((agent) => (
          <button className="agent-chip" key={agent.id} type="button" onClick={() => void handleSelectAgent(agent)}>
            {agent.id}
          </button>
        ))}
      </div>

      <AgentDrawer agent={selectedAgent} onClose={() => setSelectedAgent(null)} />
    </section>
  );
}
