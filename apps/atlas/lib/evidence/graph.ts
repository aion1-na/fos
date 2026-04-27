export type EvidenceNodeKind = "construct" | "claim" | "citation" | "dataset";

export interface EvidenceGraphNode {
  id: string;
  type: "default";
  position: { x: number; y: number };
  data: {
    label: string;
    kind: EvidenceNodeKind;
    construct?: string;
    sourceId?: string;
    confidenceLabel?: "draft" | "advisor_reviewed" | "rejected";
  };
}

export interface EvidenceGraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export const reactFlowNodes: EvidenceGraphNode[] = [
  {
    id: "construct-social-capital",
    type: "default",
    position: { x: 0, y: 40 },
    data: { label: "social capital", kind: "construct", construct: "social_capital" },
  },
  {
    id: "claim-mentoring-meaning",
    type: "default",
    position: { x: 260, y: 40 },
    data: {
      label: "claim_mentoring_meaning_v0",
      kind: "claim",
      construct: "social_capital",
      sourceId: "src_mentoring_eval_stub",
      confidenceLabel: "draft",
    },
  },
  {
    id: "citation-mentoring",
    type: "default",
    position: { x: 560, y: 40 },
    data: { label: "mentoring evaluation request record", kind: "citation" },
  },
  {
    id: "dataset-mentoring",
    type: "default",
    position: { x: 860, y: 40 },
    data: {
      label: "docs/data/datasets/mentoring-literature.md",
      kind: "dataset",
      sourceId: "src_mentoring_eval_stub",
    },
  },
  {
    id: "dataset-community-pathways",
    type: "default",
    position: { x: 860, y: 160 },
    data: {
      label: "docs/data/datasets/community-pathways.md",
      kind: "dataset",
      sourceId: "community-pathways",
    },
  },
];

export const reactFlowEdges: EvidenceGraphEdge[] = [
  {
    id: "construct-to-claim",
    source: "construct-social-capital",
    target: "claim-mentoring-meaning",
    label: "construct -> evidence claim",
  },
  {
    id: "claim-to-citation",
    source: "claim-mentoring-meaning",
    target: "citation-mentoring",
    label: "evidence claim -> citation",
  },
  {
    id: "citation-to-dataset",
    source: "citation-mentoring",
    target: "dataset-mentoring",
    label: "citation -> dataset",
  },
  {
    id: "construct-to-context-dataset",
    source: "construct-social-capital",
    target: "dataset-community-pathways",
    label: "construct -> dataset",
  },
];

export const graphFilters = {
  construct: ["social_capital", "community_context", "time_use_context"],
  claim: ["claim_mentoring_meaning_v0"],
  source: ["src_mentoring_eval_stub", "community-pathways"],
  confidenceLabel: ["draft", "advisor_reviewed", "rejected"],
};
