export type DatasetAccessStatus = "request_status_stub" | "approved_fixture" | "approved_production";

export interface DatasetSummary {
  canonicalDatasetName: string;
  version: string;
  accessStatus: DatasetAccessStatus;
}

export const atlasScope = {
  product: "Atlas",
  mode: "metadata-only",
  credentialPolicy: "no credentials in source control",
} as const;
