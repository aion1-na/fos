export type GateStatus = "green" | "amber" | "red";

export type HeadlineClaim = {
  id: string;
  claim: string;
  e_value: number;
  distributional_fidelity: { status: GateStatus; ks: number };
  seed_stability_variance: number;
  drift_status: GateStatus;
  gate: GateStatus;
};

export type ValidationPayload = {
  run_id: string;
  report_id: string;
  status: "passed" | "blocked";
  brief_export_blocked: boolean;
  headline_claims: HeadlineClaim[];
  audit_log: Array<{ event: string; artifact: string }>;
};

export type CausalPathway = {
  id: string;
  label: string;
  shapley_value: number;
  confidence_interval: [number, number];
  evidence_claim_id: string | null;
  calibrated: boolean;
};

export type CausalTracePayload = {
  run_id: string;
  pathways: CausalPathway[];
  branches: Array<{ id: string; label: string; delta: number }>;
  subgroups: Array<{ label: string; n: number; effect: number; ci: [number, number] }>;
  unintended_consequences: Array<{ label: string; severity: GateStatus; note: string }>;
  representative_agent: {
    id: string;
    summary: string;
    domain_scores: Record<string, number>;
  };
};

export type SavedFinding = {
  id: string;
  run_id: string;
  title: string;
  claim: string;
  source: "validate" | "explore";
  artifact_refs: string[];
  assumptions: string[];
  override?: Record<string, unknown> | null;
};
