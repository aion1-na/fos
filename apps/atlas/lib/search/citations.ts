export interface SearchCitation {
  id: string;
  kind: "dataset_card" | "codebook" | "evidence_claim";
  title: string;
  citation: string;
  provenanceLink: string;
  signoffStatus: "draft" | "pending_advisor_review" | "advisor_reviewed";
}

export const searchableCitations: SearchCitation[] = [
  {
    id: "community-pathways-card",
    kind: "dataset_card",
    title: "Community Pathways",
    citation: "FOS data workstream. Community Pathways dataset card, fixture release.",
    provenanceLink: "docs/data/datasets/community-pathways.md",
    signoffStatus: "pending_advisor_review",
  },
  {
    id: "constructs-v0.1",
    kind: "codebook",
    title: "Construct Dictionary v0.1",
    citation: "FOS data workstream. Construct dictionary v0.1.",
    provenanceLink: "codebooks/constructs.yaml",
    signoffStatus: "pending_advisor_review",
  },
  {
    id: "claim_mentoring_meaning_v0",
    kind: "evidence_claim",
    title: "Mentoring and meaning evidence claim",
    citation: "FOS evidence graph. claim_mentoring_meaning_v0 request-status citation path.",
    provenanceLink: "docs/data/datasets/mentoring-literature.md",
    signoffStatus: "draft",
  },
];

export function searchCitations(query: string): SearchCitation[] {
  const normalized = query.toLowerCase();
  return searchableCitations.filter((citation) =>
    [citation.id, citation.kind, citation.title, citation.citation, citation.signoffStatus]
      .join(" ")
      .toLowerCase()
      .includes(normalized),
  );
}
