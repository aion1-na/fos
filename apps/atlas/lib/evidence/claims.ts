export interface EvidenceClaimRow {
  claimId: string;
  sourceId: string;
  treatment: string;
  outcome: string;
  population: string;
  estimate: number;
  uncertainty: number;
  riskOfBias: "low" | "medium" | "high";
  confidenceLabel: "draft" | "advisor_reviewed" | "rejected";
  datasetCard: string;
  provenanceManifest: string;
}

export const evidenceClaims: EvidenceClaimRow[] = [
  {
    claimId: "claim_paid_leave_relationships_v0",
    sourceId: "src_paid_leave_meta_stub",
    treatment: "paid leave",
    outcome: "relationships",
    population: "working caregivers",
    estimate: 0.12,
    uncertainty: 0.04,
    riskOfBias: "medium",
    confidenceLabel: "draft",
    datasetCard: "docs/data/datasets/paid-leave-literature.md",
    provenanceManifest: "request-status:paid-leave-literature",
  },
  {
    claimId: "claim_job_training_financial_v0",
    sourceId: "src_job_training_rct_stub",
    treatment: "job training",
    outcome: "financial",
    population: "low-buffer workers",
    estimate: 0.18,
    uncertainty: 0.07,
    riskOfBias: "low",
    confidenceLabel: "advisor_reviewed",
    datasetCard: "docs/data/datasets/job-training-literature.md",
    provenanceManifest: "request-status:job-training-literature",
  },
  {
    claimId: "claim_mentoring_meaning_v0",
    sourceId: "src_mentoring_eval_stub",
    treatment: "mentoring",
    outcome: "meaning",
    population: "isolated young adults",
    estimate: 0.09,
    uncertainty: 0.05,
    riskOfBias: "high",
    confidenceLabel: "draft",
    datasetCard: "docs/data/datasets/mentoring-literature.md",
    provenanceManifest: "request-status:mentoring-literature",
  },
];
