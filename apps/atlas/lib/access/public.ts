export type AtlasScope = "public" | "private";

export interface AtlasAccessDataset {
  canonicalDatasetName: string;
  label: string;
  scope: AtlasScope;
  tier: "Tier 1" | "Tier 2";
  status: "fixture" | "request_status_stub" | "approved_production";
  limitations: string;
  provenanceLink: string;
  gatedReason?: "restricted_data_access" | "license_constrained";
}

export const atlasAccessDatasets: AtlasAccessDataset[] = [
  {
    canonicalDatasetName: "community-pathways",
    label: "Community pathways",
    scope: "public",
    tier: "Tier 1",
    status: "fixture",
    limitations: "Fixture-only public aggregate context; no individual inference.",
    provenanceLink: "docs/data/datasets/community-pathways.md",
  },
  {
    canonicalDatasetName: "atus-public-time-use",
    label: "ATUS public time use",
    scope: "public",
    tier: "Tier 1",
    status: "fixture",
    limitations: "Public aggregate table placeholder; not individual diary reconstruction.",
    provenanceLink: "docs/data/datasets/atus-public-time-use.md",
  },
  {
    canonicalDatasetName: "hrs",
    label: "HRS",
    scope: "private",
    tier: "Tier 1",
    status: "request_status_stub",
    limitations: "DUA-gated; no public data rows in repository.",
    provenanceLink: "docs/data/datasets/hrs.md",
    gatedReason: "restricted_data_access",
  },
  {
    canonicalDatasetName: "commercial-labor-data",
    label: "Commercial labor data",
    scope: "private",
    tier: "Tier 1",
    status: "request_status_stub",
    limitations: "License-constrained vendor data; request-status only.",
    provenanceLink: "docs/data/datasets/commercial-labor-data.md",
    gatedReason: "license_constrained",
  },
];

export const publicAtlasDatasets = atlasAccessDatasets.filter(
  (dataset) => dataset.scope === "public" && dataset.gatedReason === undefined,
);
