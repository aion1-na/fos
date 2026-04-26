"use client";

import { useEffect, useMemo, useState } from "react";

import { RUN_ID, validationFixture } from "@/lib/validation/fixture";
import { overridesForRun, type OverrideRecord } from "@/lib/validation/overrides";

type BriefFormat = "pdf" | "docx" | "json" | "bundle";

const DEFAULT_FINDINGS = [
  "Paid leave improves relationship stability for eligible caregivers.",
  "Training plus mentoring has the largest modeled branch delta.",
];

const DEFAULT_UNCERTAINTY = [
  "One mentoring pathway is exploratory because it has no calibrated evidence claim.",
  "Benefit cliff exposure remains a red unintended consequence.",
];

const DEFAULT_EVIDENCE = ["income-security-001", "social-support-001", "validation:run_standard_001"];

function FindingSelectionPanel({
  selected,
  onToggle,
}: {
  selected: string[];
  onToggle: (finding: string) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Finding Selection</h2>
      <div className="check-grid">
        {DEFAULT_FINDINGS.map((finding) => (
          <label key={finding}>
            <input checked={selected.includes(finding)} onChange={() => onToggle(finding)} type="checkbox" />
            {finding}
          </label>
        ))}
      </div>
    </section>
  );
}

function AssumptionsEditor({
  assumptions,
  onChange,
}: {
  assumptions: string;
  onChange: (value: string) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Assumptions</h2>
      <label className="stacked-field">
        Brief assumptions
        <textarea onChange={(event) => onChange(event.target.value)} value={assumptions} />
      </label>
    </section>
  );
}

function LimitationsList() {
  return (
    <section className="run-panel">
      <h2>Uncertainty</h2>
      <ul className="brief-list">
        {DEFAULT_UNCERTAINTY.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

function CitationAttachmentTable({
  citations,
  onToggle,
}: {
  citations: string[];
  onToggle: (citation: string) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Evidence Trail</h2>
      <div className="claim-table">
        {DEFAULT_EVIDENCE.map((citation) => (
          <label className="claim-row" key={citation}>
            <input checked={citations.includes(citation)} onChange={() => onToggle(citation)} type="checkbox" />
            <span>{citation}</span>
          </label>
        ))}
      </div>
    </section>
  );
}

function FormatSelector({
  format,
  onChange,
}: {
  format: BriefFormat;
  onChange: (format: BriefFormat) => void;
}) {
  return (
    <section className="run-panel">
      <h2>Format</h2>
      <div className="segmented-control brief-format-control">
        {(["pdf", "docx", "json", "bundle"] as const).map((value) => (
          <button
            className="segment-button"
            data-active={format === value}
            key={value}
            onClick={() => onChange(value)}
            type="button"
          >
            {value}
          </button>
        ))}
      </div>
    </section>
  );
}

function ExportButton({
  assumptions,
  citations,
  findings,
  format,
}: {
  assumptions: string;
  citations: string[];
  findings: string[];
  format: BriefFormat;
}) {
  const [status, setStatus] = useState("Not exported");

  async function exportBrief() {
    const payload = {
      scenario_id: "scenario-default",
      findings,
      assumptions: assumptions.split("\n").filter(Boolean),
      uncertainty: DEFAULT_UNCERTAINTY,
      evidence_trail: citations,
      validation_status: validationFixture.status,
      citation_ids: citations,
      draft: false,
    };
    const generated = await fetch(`/runs/${RUN_ID}/brief`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!generated.ok) {
      setStatus(await generated.text());
      return;
    }
    const exported = await fetch(`/runs/${RUN_ID}/brief?format=${format}`);
    if (!exported.ok) {
      setStatus(await exported.text());
      return;
    }
    await exported.blob();
    setStatus(`Exported ${format}`);
  }

  return (
    <section className="run-panel">
      <h2>Export</h2>
      <button className="primary-button" onClick={() => void exportBrief()} type="button">
        Export brief
      </button>
      <p className="summary-line">{status}</p>
    </section>
  );
}

export default function BriefPage() {
  const [overrides, setOverrides] = useState<OverrideRecord[]>([]);
  const [selectedFindings, setSelectedFindings] = useState(DEFAULT_FINDINGS);
  const [citations, setCitations] = useState(DEFAULT_EVIDENCE);
  const [format, setFormat] = useState<BriefFormat>("json");

  useEffect(() => {
    setOverrides(overridesForRun(RUN_ID));
  }, []);

  const assumptionText = useMemo(
    () =>
      [
        "Validation gates reviewed before export.",
        ...overrides.flatMap((override) => override.assumptions),
      ].join("\n"),
    [overrides],
  );
  const [assumptions, setAssumptions] = useState(assumptionText);

  useEffect(() => {
    setAssumptions(assumptionText);
  }, [assumptionText]);

  function toggle(list: string[], value: string, update: (next: string[]) => void) {
    update(list.includes(value) ? list.filter((item) => item !== value) : [...list, value]);
  }

  return (
    <main className="workspace run-workspace" id="studio-main">
      <header className="workspace-header">
        <p className="eyebrow">Studio Stage 9</p>
        <h1>Brief</h1>
        <p className="summary-line">Export surface for findings, assumptions, evidence, validation, and reproducibility.</p>
      </header>
      <section className="run-panel red-gate-panel">
        <h2>Draft run rejected</h2>
        <p className="summary-line">Draft runs cannot produce briefs. Current export target is {RUN_ID}.</p>
      </section>
      <div className="run-grid">
        <div className="run-column">
          <FindingSelectionPanel selected={selectedFindings} onToggle={(finding) => toggle(selectedFindings, finding, setSelectedFindings)} />
          <AssumptionsEditor assumptions={assumptions} onChange={setAssumptions} />
          <LimitationsList />
        </div>
        <div className="run-column">
          <CitationAttachmentTable citations={citations} onToggle={(citation) => toggle(citations, citation, setCitations)} />
          <section className="run-panel">
            <h2>Validation Status</h2>
            <span className="status-badge" data-status="red">{validationFixture.status}</span>
          </section>
          <section className="run-panel">
            <h2>Reproducibility Manifest</h2>
            <p className="summary-line">Copied from the SimulationRun artifact during export.</p>
          </section>
          <FormatSelector format={format} onChange={setFormat} />
          <ExportButton assumptions={assumptions} citations={citations} findings={selectedFindings} format={format} />
        </div>
      </div>
    </main>
  );
}
