import type { CausalTracePayload, ValidationPayload } from "@/lib/validation/types";

export const RUN_ID = "run_standard_001";

export const validationFixture: ValidationPayload = {
  run_id: RUN_ID,
  report_id: `validation:${RUN_ID}`,
  status: "blocked",
  brief_export_blocked: true,
  headline_claims: [
    {
      id: "claim-paid-leave-relationships",
      claim: "Paid leave improves relationship stability for eligible caregivers.",
      e_value: 1.82,
      distributional_fidelity: { status: "green", ks: 0.024 },
      seed_stability_variance: 0.004,
      drift_status: "green",
      gate: "green",
    },
    {
      id: "claim-training-financial",
      claim: "Job training improves financial security for low-buffer workers.",
      e_value: 1.21,
      distributional_fidelity: { status: "amber", ks: 0.047 },
      seed_stability_variance: 0.018,
      drift_status: "amber",
      gate: "amber",
    },
    {
      id: "claim-mentoring-meaning",
      claim: "Mentoring improves meaning for isolated young adults.",
      e_value: 1.05,
      distributional_fidelity: { status: "red", ks: 0.091 },
      seed_stability_variance: 0.052,
      drift_status: "red",
      gate: "red",
    },
  ],
  audit_log: [{ event: "validation_report_persisted", artifact: `validation:${RUN_ID}` }],
};

export const causalTraceFixture: CausalTracePayload = {
  run_id: RUN_ID,
  pathways: [
    {
      id: "income-security",
      label: "Income security",
      shapley_value: 0.31,
      confidence_interval: [0.22, 0.39],
      evidence_claim_id: "income-security-001",
      calibrated: true,
    },
    {
      id: "social-support",
      label: "Social support",
      shapley_value: 0.27,
      confidence_interval: [0.18, 0.34],
      evidence_claim_id: "social-support-001",
      calibrated: true,
    },
    {
      id: "schedule-autonomy",
      label: "Schedule autonomy",
      shapley_value: 0.16,
      confidence_interval: [0.04, 0.24],
      evidence_claim_id: null,
      calibrated: false,
    },
    {
      id: "peer-modeling",
      label: "Peer modeling",
      shapley_value: 0.08,
      confidence_interval: [-0.01, 0.15],
      evidence_claim_id: null,
      calibrated: false,
    },
  ],
  branches: [
    { id: "baseline", label: "Baseline", delta: 0 },
    { id: "paid-leave", label: "Paid leave", delta: 0.07 },
    { id: "training-plus-mentoring", label: "Training plus mentoring", delta: 0.11 },
  ],
  subgroups: [
    { label: "Caregivers", n: 812, effect: 0.09, ci: [0.05, 0.13] },
    { label: "Low buffer", n: 1040, effect: 0.06, ci: [0.02, 0.1] },
    { label: "Young adults", n: 950, effect: 0.04, ci: [-0.01, 0.08] },
  ],
  unintended_consequences: [
    {
      label: "Care hours displacement",
      severity: "amber",
      note: "Some subgroups shift time from care to training.",
    },
    {
      label: "Benefit cliff exposure",
      severity: "red",
      note: "Income gains may reduce eligibility in one branch.",
    },
  ],
  representative_agent: {
    id: "agent-00421",
    summary: "Caregiver with low savings buffer and high mentoring response.",
    domain_scores: {
      happiness: 0.61,
      health: 0.58,
      meaning: 0.67,
      character: 0.63,
      relationships: 0.72,
      financial: 0.55,
    },
  },
};
