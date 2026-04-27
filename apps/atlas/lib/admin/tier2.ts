export interface Tier2AccessRequest {
  canonicalDatasetName: string;
  owner: string;
  submittedOn: string | null;
  accessStatus: "request_status_stub" | "pending" | "approved" | "rejected";
  licenseStatus: "not_approved" | "pending" | "approved" | "rejected";
  secureCompartment: string;
  updatedOn: string;
  ingestAllowed: boolean;
}

export const tier2AccessRequests: Tier2AccessRequest[] = [
  {
    canonicalDatasetName: "hrs",
    owner: "Data partnerships lead",
    submittedOn: null,
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    secureCompartment: "tier2/hrs",
    updatedOn: "2026-05-15",
    ingestAllowed: false,
  },
  {
    canonicalDatasetName: "soep",
    owner: "Data partnerships lead",
    submittedOn: null,
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    secureCompartment: "tier2/soep",
    updatedOn: "2026-05-22",
    ingestAllowed: false,
  },
  {
    canonicalDatasetName: "understanding_society",
    owner: "Data partnerships lead",
    submittedOn: null,
    accessStatus: "request_status_stub",
    licenseStatus: "not_approved",
    secureCompartment: "tier2/understanding_society",
    updatedOn: "2026-05-29",
    ingestAllowed: false,
  },
];
