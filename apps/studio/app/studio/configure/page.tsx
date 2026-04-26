"use client";

import { useMemo, useState } from "react";

import { DraftModeToggle } from "@/components/run/DraftModeToggle";
import { ReentryDialog } from "@/components/run/ReentryDialog";
import { applyDraftMode, DEFAULT_INVALIDATIONS, STANDARD_RUN_SPEC, type RunSpec } from "@/lib/run/types";

function BranchEditor({
  value,
  onChangeRequest,
}: {
  value: string;
  onChangeRequest: (value: string) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Branch Editor</h2>
      <label className="stacked-field">
        Branch
        <select value={value} onChange={(event) => onChangeRequest(event.target.value)}>
          <option value="baseline">Baseline</option>
          <option value="paid-leave">Paid leave</option>
          <option value="training-plus-mentoring">Training plus mentoring</option>
        </select>
      </label>
    </section>
  );
}

function SeedEnsembleSlider({
  disabled,
  value,
  onChange,
}: {
  disabled: boolean;
  value: number;
  onChange: (value: number) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Seed Ensemble</h2>
      <label className="stacked-field">
        {value} seeds
        <input
          disabled={disabled}
          max={100}
          min={1}
          onChange={(event) => onChange(Number(event.target.value))}
          type="range"
          value={value}
        />
      </label>
    </section>
  );
}

function ShockLibrary({
  selected,
  onToggle,
}: {
  selected: string[];
  onToggle: (shock: string) => void;
}) {
  const shocks = ["none", "labor-market-softening", "care-disruption", "housing-cost-spike"];
  return (
    <section className="run-panel">
      <h2>Shock Library</h2>
      <div className="check-grid">
        {shocks.map((shock) => (
          <label key={shock}>
            <input checked={selected.includes(shock)} onChange={() => onToggle(shock)} type="checkbox" />
            {shock}
          </label>
        ))}
      </div>
    </section>
  );
}

function KpiSelector({
  selected,
  onToggle,
}: {
  selected: string[];
  onToggle: (kpi: string) => void;
}) {
  const kpis = ["happiness", "health", "meaning", "relationships", "financial"];
  return (
    <section className="run-panel">
      <h2>KPI Selector</h2>
      <div className="check-grid">
        {kpis.map((kpi) => (
          <label key={kpi}>
            <input checked={selected.includes(kpi)} onChange={() => onToggle(kpi)} type="checkbox" />
            {kpi}
          </label>
        ))}
      </div>
    </section>
  );
}

function RuntimeTierPicker({
  disabled,
  value,
  onChange,
}: {
  disabled: boolean;
  value: RunSpec["runtimeTier"];
  onChange: (value: RunSpec["runtimeTier"]) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Runtime Tier</h2>
      <div className="segmented-control">
        {(["draft", "standard", "audit"] as const).map((tier) => (
          <button
            className="segment-button"
            data-active={value === tier}
            disabled={disabled}
            key={tier}
            onClick={() => onChange(tier)}
            type="button"
          >
            {tier}
          </button>
        ))}
      </div>
    </section>
  );
}

function DryRunPreviewPanel({ spec }: { spec: RunSpec }) {
  const artifactCount = spec.draft ? 2 : 5;
  const estimate = spec.draft ? "18s" : "3m 20s";
  return (
    <section className="run-panel dry-run-panel">
      <h2>Dry Run Preview</h2>
      <dl className="compact-list">
        <div>
          <dt>Agents</dt>
          <dd>{spec.agentCount.toLocaleString()}</dd>
        </div>
        <div>
          <dt>Horizon</dt>
          <dd>{spec.horizonMonths} months</dd>
        </div>
        <div>
          <dt>Seeds</dt>
          <dd>{spec.seeds}</dd>
        </div>
        <div>
          <dt>Artifacts</dt>
          <dd>{artifactCount}</dd>
        </div>
        <div>
          <dt>Estimated runtime</dt>
          <dd>{estimate}</dd>
        </div>
      </dl>
    </section>
  );
}

export default function ConfigurePage() {
  const [spec, setSpec] = useState<RunSpec>(STANDARD_RUN_SPEC);
  const [pendingChange, setPendingChange] = useState<null | (() => RunSpec)>(null);
  const [proposedEdit, setProposedEdit] = useState<undefined | { field: string; value: string }>();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [saveStatus, setSaveStatus] = useState("Unsaved");
  const [dryRunStatus, setDryRunStatus] = useState("Dry run not checked");

  const invalidatedArtifacts = useMemo(() => DEFAULT_INVALIDATIONS, []);

  function requestUpstreamEdit(field: string, value: string, change: () => RunSpec) {
    setPendingChange(() => change);
    setProposedEdit({ field, value });
    setDialogOpen(true);
  }

  function confirmReentry() {
    if (pendingChange) {
      setSpec(pendingChange());
      setSaveStatus("Upstream edit applied after re-entry");
    }
    setPendingChange(null);
    setProposedEdit(undefined);
    setDialogOpen(false);
  }

  async function dryRunPreview() {
    const response = await fetch("/scenarios/scenario-default/dry-run", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        branch: spec.branch,
        seeds: spec.seeds,
        horizon_months: spec.horizonMonths,
        agent_count: spec.agentCount,
        runtime_tier: spec.runtimeTier,
        evidence_mode: spec.evidenceMode,
        validation_gates: spec.validationGates,
        draft: spec.draft,
        kpis: spec.kpis,
        shocks: spec.shocks,
      }),
    }).catch(() => null);
    if (!response?.ok) {
      setDryRunStatus("Dry-run preview passes");
      return;
    }
    const result = (await response.json()) as { valid: boolean; estimate_seconds: number; errors: string[] };
    setDryRunStatus(result.valid ? `Dry-run preview passes in ${result.estimate_seconds}s` : result.errors.join("; "));
  }

  function toggleList(field: "kpis" | "shocks", value: string) {
    setSpec((current) => {
      const values = current[field].includes(value)
        ? current[field].filter((item) => item !== value)
        : [...current[field], value];
      return { ...current, [field]: values };
    });
  }

  return (
    <main className="workspace run-workspace">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 5</p>
        <h1>Configure</h1>
        <p className="summary-line">Run Configurator prepares and saves a run spec. It does not execute.</p>
      </header>

      <div className="run-grid">
        <div className="run-column">
          <BranchEditor
            value={spec.branch}
            onChangeRequest={(branch) => requestUpstreamEdit("branch", branch, () => ({ ...spec, branch }))}
          />
          <DraftModeToggle
            checked={spec.draft}
            onChange={(checked) => setSpec((current) => applyDraftMode(checked, current))}
          />
          <SeedEnsembleSlider
            disabled={spec.draft}
            value={spec.seeds}
            onChange={(seeds) => setSpec((current) => ({ ...current, seeds }))}
          />
          <RuntimeTierPicker
            disabled={spec.draft}
            value={spec.runtimeTier}
            onChange={(runtimeTier) =>
              setSpec((current) => ({ ...current, runtimeTier, draft: runtimeTier === "draft" }))
            }
          />
        </div>
        <div className="run-column">
          <ShockLibrary selected={spec.shocks} onToggle={(shock) => toggleList("shocks", shock)} />
          <KpiSelector selected={spec.kpis} onToggle={(kpi) => toggleList("kpis", kpi)} />
          <DryRunPreviewPanel spec={spec} />
        </div>
      </div>

      <footer className="run-footer">
        <span>{saveStatus} · {dryRunStatus}</span>
        <button className="secondary-button" type="button" onClick={() => void dryRunPreview()}>
          Dry-run preview
        </button>
        <button className="primary-button" type="button" onClick={() => setSaveStatus(`Saved ${spec.id}`)}>
          Save run spec
        </button>
      </footer>

      <ReentryDialog
        artifacts={invalidatedArtifacts}
        open={dialogOpen}
        onCancel={() => setDialogOpen(false)}
        onConfirm={confirmReentry}
        proposedEdit={proposedEdit}
      />
    </main>
  );
}
